"""
权限管理模块 - 接口视图

提供系统全部认证与管理接口，包括：
  - 登录 / 登出 / 用户信息获取（基于自定义 Token 认证）
  - 角色 CRUD（含权限树接口、权限配置安全策略）
  - 用户 CRUD（含层级权限保护、自我保护、super_admin 唯一性保护）

权限检查统一通过 _has_perm() 函数，该函数直接查询角色的 permissions 字段，
super_admin 角色始终返回 True，隐式个人权限对所有登录用户自动生效。
"""

import hashlib
import time

from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate

from .models import Role, SysUser
from .serializers import RoleSerializer, SysUserSerializer
from .authentication import TokenAuthentication
from .token_store import _TOKEN_STORE
from apps.inspection.responses import success, fail


# 系统基础角色名称，这些角色由系统初始化创建，不可删除、不可改名
BASE_ROLE_NAMES = ('super_admin', 'admin', 'user')

# 超级管理员角色名称，权限由代码层 ALL_PERMISSIONS 强制覆盖
SUPER_ADMIN_ROLE = 'super_admin'

# 角色层级映射：数值越大权限越高
# 用于用户管理接口的层级保护：高权限可操作低权限用户，不能操作同级或更高
ROLE_LEVEL = {
    'user': 1,
    'admin': 2,
    'super_admin': 3,
}


def _get_role_level(user):
    """
    获取用户的角色等级
    用于层级保护检查：未分配角色或自定义角色返回 0（最低级别）
    """
    if user.role and user.role.name in ROLE_LEVEL:
        return ROLE_LEVEL[user.role.name]
    return 0


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    用户登录接口

    流程：
      1. 通过 Django authenticate() 验证用户名密码
      2. 生成唯一 token 并存入内存 _TOKEN_STORE
      3. 根据角色构建权限列表（super_admin 强制拥有 ALL_PERMISSIONS）
      4. 追加隐式个人权限（user:view:self / user:update:self）
      5. 返回 token + 用户信息 + 权限列表
    """
    username = (request.data.get('username') or '').strip()
    password = (request.data.get('password') or '').strip()

    if not username:
        return fail('用户名不能为空')
    if not password:
        return fail('密码不能为空')

    user = authenticate(username=username, password=password)
    if not user:
        return fail('用户名或密码错误')
    if not user.is_active:
        return fail('账号已被禁用')

    token = 'tk_' + hashlib.md5(
        f"{user.id}_{username}_{time.time()}".encode()
    ).hexdigest()

    role_data = None
    permissions = []
    if user.role:
        role_data = {'id': user.role.id, 'name': user.role.name}
        if user.role.name == SUPER_ADMIN_ROLE:
            permissions = _get_all_permissions()
        elif user.role.permissions:
            permissions = list(user.role.permissions)
        else:
            permissions = [user.role.name]

    for perm in IMPLICIT_SELF_PERMISSIONS:
        if perm not in permissions:
            permissions.append(perm)

    user_info = {
        'id': user.id,
        'username': user.username,
        'nickname': user.real_name or user.username,
        'phone': user.phone,
        'role': role_data
    }
    _TOKEN_STORE[token] = user_info

    return success('登录成功', {
        'token': token,
        'user': user_info,
        'permissions': permissions
    })


@api_view(['POST'])
def logout_view(request):
    """用户登出，从内存 _TOKEN_STORE 中移除 token，使该 token 立即失效"""
    token = _get_token(request)
    if token:
        _TOKEN_STORE.pop(token, None)
    return success('退出成功')


@api_view(['GET'])
def userinfo_view(request):
    """
    获取当前登录用户信息（实时从数据库读取）

    设计意图：权限以后端为准，每次调用都从数据库重新读取角色和权限，
    确保角色编辑 / 删除后前端权限立即同步，避免缓存导致的权限不一致。
    """
    token = _get_token(request)
    cached_user_info = _TOKEN_STORE.get(token)
    
    if not cached_user_info:
        return fail('请先登录', code=401)
    
    try:
        user = SysUser.objects.get(id=cached_user_info['id'])

        role_data = None
        permissions = []
        if user.role:
            role_data = {'id': user.role.id, 'name': user.role.name}
            if user.role.name == SUPER_ADMIN_ROLE:
                permissions = _get_all_permissions()
            elif user.role.permissions:
                permissions = list(user.role.permissions)
            else:
                permissions = [user.role.name]

        for perm in IMPLICIT_SELF_PERMISSIONS:
            if perm not in permissions:
                permissions.append(perm)

        user_info = {
            'id': user.id,
            'username': user.username,
            'nickname': user.real_name or user.username,
            'phone': user.phone,
            'role': role_data,
            'permissions': permissions
        }
        _TOKEN_STORE[token] = user_info
        
        return success('获取用户信息成功', user_info)
    except SysUser.DoesNotExist:
        return fail('用户不存在', code=404)


def _get_token(request):
    """从 Authorization 请求头提取 token，支持 'Bearer xxx' 格式"""
    auth = request.META.get('HTTP_AUTHORIZATION', '')
    if auth.startswith('Bearer '):
        return auth[7:]
    return auth


def _is_admin(user):
    """
    检查用户是否为管理员（super_admin 或 admin）

    用于判断是否可修改角色权限配置：只有管理员才能修改角色的权限树。
    注意：这与 _can_assign_role() 不同，后者限制为用户角色分配权限。
    """
    return user.role and user.role.name in ('super_admin', 'admin')


# 管理员角色名称集合，只有这些角色可以分配用户角色
_ADMIN_ROLE_NAMES = ('super_admin', 'admin')


def _can_assign_role(user):
    """
    检查用户是否可以分配/更换用户角色

    设计约束：“分配用户角色”是独立的高权限操作，
    仅通过角色名称判断（super_admin / admin），不受自定义角色权限码影响。
    即使自定义角色被配置了 user:assign_role 权限码，此函数仍返回 False。
    """
    if not user.role:
        return False
    return user.role.name in _ADMIN_ROLE_NAMES


def _has_perm(user, perm_code):
    """
    检查用户是否拥有指定权限码

    检查顺序：
      1. 隐式权限（IMPLICIT_SELF_PERMISSIONS）→ 所有登录用户自动拥有
      2. super_admin → 拥有所有权限，直接返回 True
      3. 其他用户 → 检查角色的 permissions 字段是否包含该权限码
    """
    if perm_code in IMPLICIT_SELF_PERMISSIONS:
        return True
    if not user.role:
        return False
    if user.role.name == SUPER_ADMIN_ROLE:
        return True
    return perm_code in (user.role.permissions or [])


def _is_super_admin(user):
    """检查用户是否为超级管理员（系统最高权限，全局唯一）"""
    return user.role and user.role.name == SUPER_ADMIN_ROLE


def _check_super_admin_unique(role_id, exclude_user_id=None):
    """
    检查 super_admin 角色唯一性

    如果 role_id 指向 super_admin 角色，且已有其他用户拥有该角色，返回错误信息。
    exclude_user_id 用于编辑场景：排除当前被编辑用户后再检查是否冲突。
    """
    try:
        role = Role.objects.get(id=role_id)
    except Role.DoesNotExist:
        return None
    
    if role.name != SUPER_ADMIN_ROLE:
        return None
    
    qs = SysUser.objects.filter(role__name=SUPER_ADMIN_ROLE)
    if exclude_user_id:
        qs = qs.exclude(id=exclude_user_id)
    
    if qs.exists():
        return '超级管理员角色唯一，系统中已存在超级管理员'
    return None


# 系统全量权限码（代码层固定，super_admin 始终拥有）
ALL_PERMISSIONS = [
    'role:view', 'role:create', 'role:update', 'role:delete', 'role:assign',
    'user:view', 'user:create', 'user:update', 'user:delete',
    'user:assign_role',
    'user:view:self', 'user:update:self',
    'alert:view', 'alert:handle', 'alert:delete',
    'drone:view', 'drone:control', 'drone:task'
]

# 所有登录用户隐式拥有的权限（无需配置，自动授予）
IMPLICIT_SELF_PERMISSIONS = ['user:view:self', 'user:update:self']


def _get_all_permissions():
    """
    获取所有权限码列表（代码层固定）
    super_admin 角色永远拥有这些权限，不受数据库配置影响
    """
    return ALL_PERMISSIONS.copy()


class RoleViewSet(viewsets.ModelViewSet):
    """
    角色管理 ViewSet

    提供角色 CRUD 和权限树查询接口。
    安全策略：
      - 基础角色（super_admin / admin / user）不可删除、不可改名、权限不可修改
      - super_admin 权限由代码层 ALL_PERMISSIONS 强制覆盖，数据库配置无效
      - 非管理员角色自动剥离管理员专属权限（user:assign_role / role:assign）
      - 删除角色前自动解绑关联用户（role_id 置空），避免外键悬挂
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def list(self, request, *args, **kwargs):
        """查询角色列表，无 role:view 权限返回 403"""
        if not _has_perm(request.user, 'role:view'):
            return fail('无权访问角色管理', code=403)
        response = super().list(request, *args, **kwargs)
        return success(data=response.data)

    def retrieve(self, request, *args, **kwargs):
        """查询单条角色详情，无 role:view 权限返回 403"""
        if not _has_perm(request.user, 'role:view'):
            return fail('无权访问角色管理', code=403)
        response = super().retrieve(request, *args, **kwargs)
        return success(data=response.data)

    @action(detail=False, methods=['get'])
    def permission_tree(self, request):
        """
        获取权限树结构

        返回所有可用的权限码，按模块分组。
        用于前端角色权限配置界面展示。
        无 role:view 权限返回 403
        """
        if not _has_perm(request.user, 'role:view'):
            return fail('无权访问权限配置', code=403)
        tree = [
            {
                'id': 'role',
                'label': '角色管理',
                'children': [
                    {'id': 'role:view', 'label': '查看角色列表'},
                    {'id': 'role:create', 'label': '创建角色'},
                    {'id': 'role:update', 'label': '编辑角色'},
                    {'id': 'role:delete', 'label': '删除角色'},
                    # role:assign 为管理员专属权限，不出现在角色权限编辑树中
                ]
            },
            {
                'id': 'user',
                'label': '用户管理（管理他人）',
                'children': [
                    {'id': 'user:view', 'label': '查看用户列表'},
                    {'id': 'user:create', 'label': '创建用户'},
                    {'id': 'user:update', 'label': '编辑用户信息'},
                    {'id': 'user:delete', 'label': '删除用户'},
                    # user:assign_role 为管理员专属权限，不出现在角色权限编辑树中
                ]
            },
            {
                'id': 'alert',
                'label': '告警管理',
                'children': [
                    {'id': 'alert:view', 'label': '查看告警'},
                    {'id': 'alert:handle', 'label': '处理告警'},
                    {'id': 'alert:delete', 'label': '删除告警'},
                ]
            },
            {
                'id': 'drone',
                'label': '无人机管控',
                'children': [
                    {'id': 'drone:view', 'label': '查看无人机状态'},
                    {'id': 'drone:control', 'label': '控制无人机'},
                    {'id': 'drone:task', 'label': '任务管理'},
                ]
            }
        ]
        return success('获取权限树成功', tree)

    def create(self, request, *args, **kwargs):
        """
        创建角色
        
        安全策略：
        1. 需要 role:create 权限
        2. 非管理员角色不允许拥有 user:assign_role / role:assign 权限
        3. 非管理员不可设置权限配置（仅管理员可配置角色权限）
        """
        if not _has_perm(request.user, 'role:create'):
            return fail('无权创建角色', code=403)
        
        # 非管理员角色自动剥离管理员专属权限（user:assign_role, role:assign）
        role_name = request.data.get('name', '')
        if role_name not in _ADMIN_ROLE_NAMES and 'permissions' in request.data:
            perms = request.data['permissions']
            if isinstance(perms, list):
                admin_only = {'user:assign_role', 'role:assign'}
                request.data['permissions'] = [p for p in perms if p not in admin_only]
        
        response = super().create(request, *args, **kwargs)
        return success('角色创建完成', data=response.data)

    def destroy(self, request, *args, **kwargs):
        """
        删除角色：先解绑关联用户，再物理删除角色
        
        安全策略：
        1. 需要 role:delete 权限
        2. 基础角色（super_admin / admin / user）不可删除
        """
        if not _has_perm(request.user, 'role:delete'):
            return fail('无权删除角色', code=403)
        
        instance = self.get_object()
        
        # 基础角色不可删除
        if instance.name in BASE_ROLE_NAMES:
            return fail(f'基础角色「{instance.name}」不可删除', code=403)
        
        # 1. 解绑所有关联该角色的用户（role_id 置空）
        SysUser.objects.filter(role_id=instance.id).update(role=None)
        # 2. 物理删除角色
        instance.delete()
        return success('角色删除完成')

    def update(self, request, *args, **kwargs):
        """
        更新角色信息（含权限配置）
        
        安全策略：
        1. 需要 role:update 权限
        2. 基础角色（super_admin / admin / user）的名称、描述、权限均不可修改
        3. super_admin 角色的权限永远固定为 ALL_PERMISSIONS
        4. 非管理员不可修改权限配置（仅管理员可配置角色权限）
        """
        if not _has_perm(request.user, 'role:update'):
            return fail('无权修改角色', code=403)
        
        instance = self.get_object()
        
        # 非管理员不可修改权限配置（仅 super_admin / admin 可以）
        if not _is_admin(request.user) and 'permissions' in request.data:
            return fail('仅管理员可以修改角色权限配置', code=403)
        
        # 基础角色的名称、描述、权限均不可修改
        if instance.name in BASE_ROLE_NAMES:
            if 'name' in request.data and request.data['name'] != instance.name:
                return fail(f'基础角色「{instance.name}」的名称不可修改', code=403)
            if 'desc' in request.data and request.data['desc'] != instance.desc:
                return fail(f'基础角色「{instance.name}」的描述不可修改', code=403)
            if 'permissions' in request.data:
                return fail(f'基础角色「{instance.name}」的权限不可修改', code=403)
        
        # 如果是 super_admin 角色，强制设置权限为代码层固定的权限
        if instance.name == SUPER_ADMIN_ROLE:
            request.data['permissions'] = _get_all_permissions()
        elif instance.name not in _ADMIN_ROLE_NAMES and 'permissions' in request.data:
            # 非管理员角色自动剥离管理员专属权限（user:assign_role, role:assign）
            perms = request.data['permissions']
            if isinstance(perms, list):
                admin_only = {'user:assign_role', 'role:assign'}
                request.data['permissions'] = [p for p in perms if p not in admin_only]
        
        response = super().update(request, *args, **kwargs)
        return success('角色信息修改完成', data=response.data)

    def partial_update(self, request, *args, **kwargs):
        """
        部分更新角色（PATCH 请求）
        
        同样需要应用权限检查和基础角色保护
        非管理员不可修改权限配置
        """
        if not _has_perm(request.user, 'role:update'):
            return fail('无权修改角色', code=403)
        
        instance = self.get_object()
        
        # 非管理员不可修改权限配置（仅 super_admin / admin 可以）
        if not _is_admin(request.user) and 'permissions' in request.data:
            return fail('仅管理员可以修改角色权限配置', code=403)
        
        # 基础角色的名称、描述、权限均不可修改
        if instance.name in BASE_ROLE_NAMES:
            if 'name' in request.data and request.data['name'] != instance.name:
                return fail(f'基础角色「{instance.name}」的名称不可修改', code=403)
            if 'desc' in request.data and request.data['desc'] != instance.desc:
                return fail(f'基础角色「{instance.name}」的描述不可修改', code=403)
            if 'permissions' in request.data:
                return fail(f'基础角色「{instance.name}」的权限不可修改', code=403)
        
        # 如果是 super_admin 角色，强制设置权限为代码层固定的权限
        if instance.name == SUPER_ADMIN_ROLE:
            if 'permissions' in request.data:
                request.data['permissions'] = _get_all_permissions()
        elif instance.name not in _ADMIN_ROLE_NAMES and 'permissions' in request.data:
            # 非管理员角色自动剥离管理员专属权限（user:assign_role, role:assign）
            perms = request.data['permissions']
            if isinstance(perms, list):
                admin_only = {'user:assign_role', 'role:assign'}
                request.data['permissions'] = [p for p in perms if p not in admin_only]
        
        response = super().partial_update(request, *args, **kwargs)
        return success('角色信息修改完成', data=response.data)


class SysUserViewSet(viewsets.ModelViewSet):
    """
    用户管理 ViewSet

    提供用户 CRUD、角色分配、个人资料和密码修改接口。
    安全策略：
      - 层级保护：高权限可操作低权限用户，不能操作同级或更高
      - 自我保护：不可修改自己的角色 / 激活状态，防止自降权或自禁用
      - super_admin 唯一性保护：不能降级、禁用、删除最后一个超级管理员
      - 角色分配（user:assign_role）仅限 super_admin / admin，不受自定义权限码影响
    筛选：支持按角色 ID 过滤、按账号 / 姓名模糊搜索
    """

    queryset = SysUser.objects.all().order_by('-create_time')
    serializer_class = SysUserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role']
    search_fields = ['username', 'real_name']

    def list(self, request, *args, **kwargs):
        """
        查询用户列表
        
        权限控制：
        - 有 user:view 权限：返回全量用户列表
        - 无 user:view 权限（如 user 角色）：仅返回自身信息
        """
        if not _has_perm(request.user, 'user:view'):
            # 无查看权限，仅返回自身数据
            self.queryset = SysUser.objects.filter(id=request.user.id)
        response = super().list(request, *args, **kwargs)
        return success(data=response.data)

    def retrieve(self, request, *args, **kwargs):
        """
        查询单条用户详情
        
        数据权限：无 user:view 权限只能查看自身
        """
        instance = self.get_object()
        if not _has_perm(request.user, 'user:view') and instance.id != request.user.id:
            return fail('无权查看其他用户信息', code=403)
        response = super().retrieve(request, *args, **kwargs)
        return success(data=response.data)

    @action(detail=False, methods=['get', 'put'])
    def profile(self, request):
        """
        基本资料管理（任何登录用户均可使用）

        GET: 获取自身信息（需要 user:view:self 权限）
        PUT: 修改自身姓名、电话（需要 user:update:self 权限）
        不允许修改角色、激活状态、密码等
        """
        user = request.user

        if request.method == 'GET':
            # 检查个人查看权限（所有登录用户隐式拥有）
            if not _has_perm(user, 'user:view:self'):
                return fail('无权查看个人信息', code=403)
            serializer = self.get_serializer(user)
            return success(data=serializer.data)

        # PUT：检查个人修改权限（所有登录用户隐式拥有）
        if not _has_perm(user, 'user:update:self'):
            return fail('无权修改个人信息', code=403)
        
        # 只允许修改 real_name / phone
        allowed_fields = {'real_name', 'phone'}
        cleaned = {k: v for k, v in request.data.items() if k in allowed_fields}

        for field, value in cleaned.items():
            setattr(user, field, value)
        user.save()

        serializer = self.get_serializer(user)
        return success('基本资料修改完成', data=serializer.data)

    @action(detail=False, methods=['put'])
    def change_password(self, request):
        """
        修改密码（任何登录用户均可使用）

        需要验证旧密码，新密码不少于 6 位
        """
        user = request.user
        old_password = request.data.get('old_password', '')
        new_password = request.data.get('new_password', '')

        if not old_password:
            return fail('请输入旧密码')
        if not new_password:
            return fail('请输入新密码')
        if len(new_password) < 6:
            return fail('新密码至少 6 位')
        if not user.check_password(old_password):
            return fail('旧密码错误')

        from django.contrib.auth.hashers import make_password
        user.password = make_password(new_password)
        user.save()
        return success('密码修改成功')

    def create(self, request, *args, **kwargs):
        """
        新增用户
        
        安全策略：
        1. super_admin 角色唯一，不能分配给第二个用户
        2. 只能创建角色等级低于自己的用户
        3. 分配角色需要 user:assign_role 权限，否则忽略 role_id
        4. 需要 user:create 权限
        """
        if not _has_perm(request.user, 'user:create'):
            return fail('无权添加用户', code=403)
        
        # 检查是否可以分配角色（仅管理员角色：super_admin / admin）
        if not _can_assign_role(request.user):
            request.data.pop('role_id', None)
            request.data.pop('role', None)
        else:
            # 层级权限：只能创建角色等级低于自己的用户
            role_id = request.data.get('role_id') or request.data.get('role')
            if role_id:
                try:
                    target_role = Role.objects.get(id=role_id)
                    target_level = ROLE_LEVEL.get(target_role.name, 0)
                    if target_level >= _get_role_level(request.user):
                        return fail('无权创建同级或更高权限的用户', code=403)
                except Role.DoesNotExist:
                    pass
                
                # 检查 super_admin 唯一性
                err = _check_super_admin_unique(role_id)
                if err:
                    return fail(err, code=403)
        
        response = super().create(request, *args, **kwargs)
        return success('用户新增完成', data=response.data)

    def update(self, request, *args, **kwargs):
        """
        编辑用户信息、更换角色
        
        安全策略：
        1. 高权限可操作低权限用户，不能操作同级或更高
        2. 不能修改自己的角色（防止自降权）
        3. 不能修改自己的激活状态（防止自禁用）
        4. 最后一个 super_admin 不能被降级或禁用
        5. 编辑自己时允许修改姓名、电话、密码
        6. 修改角色需要 user:assign_role 权限，否则忽略 role_id
        7. 需要 user:update 权限
        """
        if not _has_perm(request.user, 'user:update'):
            return fail('无权编辑用户', code=403)
        
        instance = self.get_object()
        
        # 层级权限检查：不能操作同级或更高权限的用户（编辑自己除外）
        if instance.id != request.user.id:
            target_level = _get_role_level(instance)
            if target_level >= _get_role_level(request.user):
                return fail('无权操作同级或更高权限的用户', code=403)
        
        # 检查是否可以分配角色（仅管理员角色：super_admin / admin）
        has_assign_role = _can_assign_role(request.user)
        if not has_assign_role:
            request.data.pop('role_id', None)
            request.data.pop('role', None)
        else:
            # 检查 super_admin 唯一性（如果尝试更换角色为 super_admin）
            new_role_id = request.data.get('role') or request.data.get('role_id')
            if new_role_id and str(new_role_id) != 'null':
                err = _check_super_admin_unique(new_role_id, exclude_user_id=instance.id)
                if err:
                    return fail(err, code=403)
        
        # 自我保护机制：禁止修改自己的关键信息
        if instance.id == request.user.id:
            # 检查是否尝试修改角色
            if 'role' in request.data or 'role_id' in request.data:
                return fail('不能修改自己的角色', code=403)
            
            # 检查是否尝试修改激活状态
            if 'is_active' in request.data:
                return fail('不能修改自己的激活状态', code=403)
        
        # 保护唯一的 super_admin：不能降级或禁用
        # 仅当请求中实际包含 role_id 时才检查角色变更
        if instance.role and instance.role.name == SUPER_ADMIN_ROLE:
            new_role_id = request.data.get('role') or request.data.get('role_id')
            has_role_change = 'role' in request.data or 'role_id' in request.data
            if has_role_change:
                if new_role_id is None or str(new_role_id) == 'null':
                    # 尝试移除 super_admin 角色
                    sa_count = SysUser.objects.filter(
                        role__name=SUPER_ADMIN_ROLE,
                        is_active=True
                    ).count()
                    if sa_count <= 1:
                        return fail('不能移除最后一个超级管理员的角色', code=403)
                else:
                    try:
                        new_role_int = int(new_role_id)
                    except (ValueError, TypeError):
                        return fail('role_id 必须为有效整数', code=400)
                    if new_role_int != instance.role.id:
                        # 尝试更换为非 super_admin 角色
                        sa_count = SysUser.objects.filter(
                            role__name=SUPER_ADMIN_ROLE,
                            is_active=True
                        ).count()
                        if sa_count <= 1:
                            return fail('不能将最后一个超级管理员更换为其他角色', code=403)
            
            # 检查是否尝试禁用
            if 'is_active' in request.data and not request.data['is_active']:
                sa_count = SysUser.objects.filter(
                    role__name=SUPER_ADMIN_ROLE,
                    is_active=True
                ).count()
                if sa_count <= 1:
                    return fail('不能禁用最后一个超级管理员账号', code=403)
        
        response = super().update(request, *args, **kwargs)
        return success('用户信息修改完成', data=response.data)

    def partial_update(self, request, *args, **kwargs):
        """
        部分更新用户（PATCH 请求）
        
        同样需要应用层级权限、自我保护机制和 super_admin 保护
        修改角色需要 user:assign_role 权限
        """
        if not _has_perm(request.user, 'user:update'):
            return fail('无权编辑用户', code=403)
        
        instance = self.get_object()
        
        # 层级权限检查：不能操作同级或更高权限的用户（编辑自己除外）
        if instance.id != request.user.id:
            target_level = _get_role_level(instance)
            if target_level >= _get_role_level(request.user):
                return fail('无权操作同级或更高权限的用户', code=403)
        
        # 检查是否可以分配角色（仅管理员角色：super_admin / admin）
        if not _can_assign_role(request.user):
            request.data.pop('role_id', None)
            request.data.pop('role', None)
        else:
            # 检查 super_admin 唯一性（如果尝试更换角色为 super_admin）
            new_role_id = request.data.get('role') or request.data.get('role_id')
            if new_role_id and str(new_role_id) != 'null':
                err = _check_super_admin_unique(new_role_id, exclude_user_id=instance.id)
                if err:
                    return fail(err, code=403)
        
        # 自我保护机制：禁止修改自己的关键信息
        if instance.id == request.user.id:
            if 'role' in request.data or 'role_id' in request.data:
                return fail('不能修改自己的角色', code=403)
            if 'is_active' in request.data:
                return fail('不能修改自己的激活状态', code=403)
        
        # 保护唯一的 super_admin
        if instance.role and instance.role.name == SUPER_ADMIN_ROLE:
            has_role_change = 'role' in request.data or 'role_id' in request.data
            if has_role_change:
                new_role_id = request.data.get('role') or request.data.get('role_id')
                if new_role_id is not None and str(new_role_id) != 'null':
                    try:
                        new_role_int = int(new_role_id)
                    except (ValueError, TypeError):
                        return fail('role_id 必须为有效整数', code=400)
                    if new_role_int != instance.role.id:
                        sa_count = SysUser.objects.filter(
                            role__name=SUPER_ADMIN_ROLE,
                            is_active=True
                        ).count()
                        if sa_count <= 1:
                            return fail('不能将最后一个超级管理员更换为其他角色', code=403)
            
            if 'is_active' in request.data and not request.data['is_active']:
                sa_count = SysUser.objects.filter(
                    role__name=SUPER_ADMIN_ROLE,
                    is_active=True
                ).count()
                if sa_count <= 1:
                    return fail('不能禁用最后一个超级管理员账号', code=403)
        
        response = super().partial_update(request, *args, **kwargs)
        return success('用户信息修改完成', data=response.data)

    def destroy(self, request, *args, **kwargs):
        """
        删除系统用户

        安全策略：
        1. 不能删除自己
        2. 不能删除同级或更高权限的用户
        3. 不能删除最后一个超级管理员
        4. 需要 user:delete 权限
        """
        if not _has_perm(request.user, 'user:delete'):
            return fail('无权删除用户', code=403)
        instance = self.get_object()

        # 1. 不能删除自己
        if instance.id == request.user.id:
            return fail('不能删除当前登录用户')

        # 2. 层级权限：不能删除同级或更高权限的用户
        target_level = _get_role_level(instance)
        if target_level >= _get_role_level(request.user):
            return fail('无权删除同级或更高权限的用户', code=403)

        # 3. 检查是否是最后一个超级管理员
        if instance.role and instance.role.name == SUPER_ADMIN_ROLE:
            sa_count = SysUser.objects.filter(
                role__name=SUPER_ADMIN_ROLE,
                is_active=True
            ).count()
            if sa_count <= 1:
                return fail('不能删除最后一个超级管理员账号')

        instance.delete()
        return success('用户删除完成')
