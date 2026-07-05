"""
权限管理模块 - 路由配置

接口前缀: /api/system/

认证接口（无需登录）：
  POST login      用户登录，返回 token + 用户信息 + 权限列表
  POST logout     用户登出，清除服务端 token

用户信息接口（需登录）：
  GET  userinfo   实时从数据库读取当前用户信息和权限

CRUD 接口（需登录，由 DefaultRouter 自动生成 RESTful 路由）：
  /roles/         角色管理（RoleViewSet）
  /users/         用户管理（SysUserViewSet）
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoleViewSet, SysUserViewSet, login_view, logout_view, userinfo_view

router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'users', SysUserViewSet)

urlpatterns = [
    path('login', login_view, name='system-login'),
    path('logout', logout_view, name='system-logout'),
    path('userinfo', userinfo_view, name='system-userinfo'),
    path('', include(router.urls)),
]
