"""
权限管理模块 - 接口视图

提供登录认证、角色、用户管理 CRUD 接口。
所有接口需登录访问（permission_classes = [IsAuthenticated]）。
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


# ── 登录认证接口 ──────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    用户登录（查数据库）

    接收 username/password，验证成功后生成 token 并返回用户信息 + 权限。
    """
    username = (request.data.get('username') or '').strip()
    password = (request.data.get('password') or '').strip()

    if not username:
        return fail('用户名不能为空')
    if not password:
        return fail('密码不能为空')

    # 从数据库验证用户
    user = authenticate(username=username, password=password)
    if not user:
        return fail('用户名或密码错误')

    if not user.is_active:
        return fail('账号已被禁用')

    # 生成 token
    token = 'tk_' + hashlib.md5(
        f"{user.id}_{username}_{time.time()}".encode()
    ).hexdigest()

    # 构建用户信息
    role_data = None
    permissions = []
    # 检查角色是否存在
    if user.role:
        role_data = {'id': user.role.id, 'name': user.role.name}
        # admin 角色强制拥有所有权限（后端 override）
        if user.role.name == 'admin':
            permissions = _get_all_permissions()
        else:
            # 从角色的 permissions 字段获取权限码列表
            if user.role.permissions and len(user.role.permissions) > 0:
                permissions = user.role.permissions
            else:
                permissions = [user.role.name]

    user_info = {
        'id': user.id,
        'username': user.username,
        'nickname': user.real_name or user.username,
        'email': user.email,
        'phone': user.phone,
        'role': role_data
    }

    # 存储 token
    _TOKEN_STORE[token] = user_info

    return success('登录成功', {
        'token': token,
        'user': user_info,
        'permissions': permissions
    })


@api_view(['POST'])
def logout_view(request):
    """用户登出，清除 token"""
    token = _get_token(request)
    if token:
        _TOKEN_STORE.pop(token, None)
    return success('退出成功')


@api_view(['GET'])
def userinfo_view(request):
    """
    获取当前登录用户信息（实时从数据库读取）
    
    每次调用都从数据库重新读取用户角色和权限，确保权限变更后立即生效。
    """
    token = _get_token(request)
    cached_user_info = _TOKEN_STORE.get(token)
    
    if not cached_user_info:
        return fail('请先登录', code=401)
    
    # 从数据库实时读取用户信息和权限
    try:
        user = SysUser.objects.get(id=cached_user_info['id'])
        
        # 构建最新的用户信息
        role_data = None
        permissions = []
        
        if user.role:
            role_data = {'id': user.role.id, 'name': user.role.name}
            
            # admin 角色强制拥有所有权限（后端 override）
            if user.role.name == 'admin':
                permissions = _get_all_permissions()
            else:
                # 从角色的 permissions 字段获取权限码列表
                if user.role.permissions and len(user.role.permissions) > 0:
                    permissions = user.role.permissions
                else:
                    permissions = [user.role.name]
        
        user_info = {
            'id': user.id,
            'username': user.username,
            'nickname': user.real_name or user.username,
            'email': user.email,
            'phone': user.phone,
            'role': role_data,
            'permissions': permissions  # 添加权限字段
        }
        
        # 更新 token store 中的缓存
        _TOKEN_STORE[token] = user_info
        
        return success('获取用户信息成功', user_info)
    except SysUser.DoesNotExist:
        return fail('用户不存在', code=404)


def _get_token(request):
    """从请求头提取 token"""
    auth = request.META.get('HTTP_AUTHORIZATION', '')
    if auth.startswith('Bearer '):
        return auth[7:]
    return auth


def _is_admin(user):
    """检查用户是否为管理员"""
    return user.role and user.role.name == 'admin'


# ── 角色/用户管理 ──────────────────────────────────────

# 定义系统所有可用权限码（代码层固定）
ALL_PERMISSIONS = [
    # 角色管理
    'role:view', 'role:create', 'role:update', 'role:delete', 'role:assign',
    # 用户管理
    'user:view', 'user:create', 'user:update', 'user:delete',
    # 告警管理
    'alert:view', 'alert:handle', 'alert:delete',
    # 无人机管控
    'drone:view', 'drone:control', 'drone:task'
]


def _get_all_permissions():
    """
    获取所有权限码列表（代码层固定）
    admin 角色永远拥有这些权限，不受数据库配置影响
    """
    return ALL_PERMISSIONS.copy()


class RoleViewSet(viewsets.ModelViewSet):
    """
    角色管理接口

    管理系统角色，用户分配角色使用。
    删除角色时自动解绑关联用户（role_id 置空），再物理删除角色。
    接口前缀: /api/system/roles/
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @action(detail=False, methods=['get'])
    def permission_tree(self, request):
        """
        获取权限树结构

        返回所有可用的权限码，按模块分组。
        用于前端角色权限配置界面展示。
        """
        tree = [
            {
                'id': 'role',
                'label': '角色管理',
                'children': [
                    {'id': 'role:view', 'label': '查看角色列表'},
                    {'id': 'role:create', 'label': '创建角色'},
                    {'id': 'role:update', 'label': '编辑角色'},
                    {'id': 'role:delete', 'label': '删除角色'},
                    {'id': 'role:assign', 'label': '分配角色权限'},
                ]
            },
            {
                'id': 'user',
                'label': '用户管理',
                'children': [
                    {'id': 'user:view', 'label': '查看用户列表'},
                    {'id': 'user:create', 'label': '创建用户'},
                    {'id': 'user:update', 'label': '编辑用户'},
                    {'id': 'user:delete', 'label': '删除用户'},
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

    def destroy(self, request, *args, **kwargs):
        """
        删除角色：先解绑关联用户，再物理删除角色
        """
        instance = self.get_object()
        # 1. 解绑所有关联该角色的用户（role_id 置空）
        SysUser.objects.filter(role_id=instance.id).update(role=None)
        # 2. 物理删除角色
        instance.delete()
        return success('角色删除完成')

    def update(self, request, *args, **kwargs):
        """
        更新角色信息（含权限配置）
        
        安全策略：
        1. admin 角色的权限永远固定为 ALL_PERMISSIONS，不允许修改
        2. 其他角色可以正常修改权限
        """
        instance = self.get_object()
        
        # 如果是 admin 角色，强制设置权限为代码层固定的权限
        if instance.name == 'admin':
            # 无论前端传什么，都强制使用固定权限
            request.data['permissions'] = _get_all_permissions()
        
        response = super().update(request, *args, **kwargs)
        return success('角色信息修改完成', data=response.data)

    def partial_update(self, request, *args, **kwargs):
        """
        部分更新角色（PATCH 请求）
        
        同样需要保护 admin 角色的权限不被修改
        """
        instance = self.get_object()
        
        # 如果是 admin 角色，强制设置权限为代码层固定的权限
        if instance.name == 'admin':
            # 无论前端传什么，都强制使用固定权限
            if 'permissions' in request.data:
                request.data['permissions'] = _get_all_permissions()
        
        response = super().partial_update(request, *args, **kwargs)
        return success('角色信息修改完成', data=response.data)


class SysUserViewSet(viewsets.ModelViewSet):
    """
    用户管理接口

    提供用户 CRUD 和角色分配功能。
    支持按角色筛选、按账号/姓名模糊搜索。
    接口前缀: /api/system/users/
    """

    queryset = SysUser.objects.all().order_by('-create_time')
    serializer_class = SysUserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role']
    search_fields = ['username', 'real_name']

    def list(self, request, *args, **kwargs):
        """查询用户列表，统一封装返回格式"""
        response = super().list(request, *args, **kwargs)
        return success(data=response.data)

    def retrieve(self, request, *args, **kwargs):
        """查询单条用户详情"""
        response = super().retrieve(request, *args, **kwargs)
        return success(data=response.data)

    def create(self, request, *args, **kwargs):
        """新增用户（仅管理员）"""
        if not _is_admin(request.user):
            return fail('仅管理员可添加用户', code=403)
        response = super().create(request, *args, **kwargs)
        return success('用户新增完成', data=response.data)

    def update(self, request, *args, **kwargs):
        """
        编辑用户信息、更换角色（仅管理员）
        
        安全策略：
        1. 仅 admin 可编辑用户
        2. 不能修改自己的角色（防止自降权）
        3. 不能修改自己的激活状态（防止自禁用）
        4. 最后一个 admin 不能被降级或禁用
        """
        if not _is_admin(request.user):
            return fail('仅管理员可编辑用户', code=403)
        
        instance = self.get_object()
        
        # 自我保护机制：禁止修改自己的关键信息
        if instance.id == request.user.id:
            # 检查是否尝试修改角色
            if 'role' in request.data or 'role_id' in request.data:
                return fail('不能修改自己的角色', code=403)
            
            # 检查是否尝试修改激活状态
            if 'is_active' in request.data:
                return fail('不能修改自己的激活状态', code=403)
        
        # 保护最后一个 admin：不能降级或禁用
        if instance.role and instance.role.name == 'admin':
            # 检查是否尝试降级（移除 admin 角色）
            new_role_id = request.data.get('role') or request.data.get('role_id')
            if new_role_id is None or str(new_role_id) == 'null':
                # 尝试移除角色
                admin_count = SysUser.objects.filter(
                    role__name='admin',
                    is_active=True
                ).count()
                if admin_count <= 1:
                    return fail('不能降级最后一个管理员账号', code=403)
            elif int(new_role_id) != instance.role.id:
                # 尝试更换为非 admin 角色
                admin_count = SysUser.objects.filter(
                    role__name='admin',
                    is_active=True
                ).count()
                if admin_count <= 1:
                    return fail('不能将最后一个管理员更换为其他角色', code=403)
            
            # 检查是否尝试禁用
            if 'is_active' in request.data and not request.data['is_active']:
                admin_count = SysUser.objects.filter(
                    role__name='admin',
                    is_active=True
                ).count()
                if admin_count <= 1:
                    return fail('不能禁用最后一个管理员账号', code=403)
        
        response = super().update(request, *args, **kwargs)
        return success('用户信息修改完成', data=response.data)

    def partial_update(self, request, *args, **kwargs):
        """
        部分更新用户（PATCH 请求）
        
        同样需要应用自我保护机制和 admin 保护
        """
        if not _is_admin(request.user):
            return fail('仅管理员可编辑用户', code=403)
        
        instance = self.get_object()
        
        # 自我保护机制：禁止修改自己的关键信息
        if instance.id == request.user.id:
            if 'role' in request.data or 'role_id' in request.data:
                return fail('不能修改自己的角色', code=403)
            if 'is_active' in request.data:
                return fail('不能修改自己的激活状态', code=403)
        
        # 保护最后一个 admin
        if instance.role and instance.role.name == 'admin':
            new_role_id = request.data.get('role') or request.data.get('role_id')
            if new_role_id is not None and str(new_role_id) != 'null' and int(new_role_id) != instance.role.id:
                admin_count = SysUser.objects.filter(
                    role__name='admin',
                    is_active=True
                ).count()
                if admin_count <= 1:
                    return fail('不能将最后一个管理员更换为其他角色', code=403)
            
            if 'is_active' in request.data and not request.data['is_active']:
                admin_count = SysUser.objects.filter(
                    role__name='admin',
                    is_active=True
                ).count()
                if admin_count <= 1:
                    return fail('不能禁用最后一个管理员账号', code=403)
        
        response = super().partial_update(request, *args, **kwargs)
        return success('用户信息修改完成', data=response.data)

    def destroy(self, request, *args, **kwargs):
        """
        删除系统用户（仅管理员）

        安全策略：
        1. 不能删除自己
        2. 不能删除最后一个管理员
        """
        if not _is_admin(request.user):
            return fail('仅管理员可删除用户', code=403)
        instance = self.get_object()

        # 1. 不能删除自己
        if instance.id == request.user.id:
            return fail('不能删除当前登录用户')

        # 2. 检查是否是最后一个管理员
        if instance.role and instance.role.name == 'admin':
            admin_count = SysUser.objects.filter(
                role__name='admin',
                is_active=True
            ).count()
            if admin_count <= 1:
                return fail('不能删除最后一个管理员账号')

        instance.delete()
        return success('用户删除完成')
