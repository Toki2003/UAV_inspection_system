"""
权限管理模块 - 路由配置

接口前缀: /api/system/
- login/: 登录
- logout/: 登出
- userinfo/: 当前用户信息
- roles/: 角色管理
- users/: 用户管理
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoleViewSet, SysUserViewSet, login_view, logout_view, userinfo_view

router = DefaultRouter()
router.register(r'roles', RoleViewSet)    # 角色管理
router.register(r'users', SysUserViewSet) # 用户管理

urlpatterns = [
    # 登录认证（不需要登录）
    path('login', login_view, name='system-login'),
    path('logout', logout_view, name='system-logout'),
    path('userinfo', userinfo_view, name='system-userinfo'),
    # CRUD 路由
    path('', include(router.urls)),
]
