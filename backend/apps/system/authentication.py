"""
权限管理模块 - 自定义 Token 认证

基于登录接口生成的 token 进行身份认证，
从共享 _TOKEN_STORE 中查找 token 对应的用户信息，
并从数据库加载 SysUser 实例设置为 request.user。
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .token_store import _TOKEN_STORE


class TokenAuthentication(BaseAuthentication):
    """
    Bearer Token 认证类

    从 Authorization: Bearer <token> 头部提取 token，
    在 _TOKEN_STORE 中查找对应用户信息，
    再从数据库加载 SysUser 实例作为 request.user。
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None  # 不处理，交给下一个认证后端

        token = auth_header[7:]
        if not token:
            return None

        user_info = _TOKEN_STORE.get(token)
        if not user_info:
            raise AuthenticationFailed('token 无效或已过期，请重新登录')

        # 从数据库加载完整的 SysUser 实例
        from apps.system.models import SysUser
        try:
            user = SysUser.objects.get(id=user_info['id'])
        except SysUser.DoesNotExist:
            raise AuthenticationFailed('用户不存在')

        if not user.is_active:
            raise AuthenticationFailed('账号已被禁用')

        return (user, token)

    def authenticate_header(self, request):
        return 'Bearer'
