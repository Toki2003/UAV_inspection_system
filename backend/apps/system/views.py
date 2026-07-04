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
        # admin 角色拥有所有权限
        if user.role.name == 'admin':
            permissions = ['admin']
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
    """获取当前登录用户信息"""
    token = _get_token(request)
    user_info = _TOKEN_STORE.get(token)
    if not user_info:
        return fail('请先登录', code=401)
    return success('获取用户信息成功', user_info)


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
        """编辑用户信息、更换角色（仅管理员）"""
        if not _is_admin(request.user):
            return fail('仅管理员可编辑用户', code=403)
        response = super().update(request, *args, **kwargs)
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
