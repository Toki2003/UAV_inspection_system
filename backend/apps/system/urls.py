"""
权限管理模块 - 路由配置

接口前缀: /api/system/
- menus/: 菜单管理
- roles/: 角色管理
- users/: 用户管理
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MenuViewSet, RoleViewSet, SysUserViewSet

router = DefaultRouter()
router.register(r'menus', MenuViewSet)    # 菜单管理
router.register(r'roles', RoleViewSet)    # 角色管理
router.register(r'users', SysUserViewSet) # 用户管理

urlpatterns = [
    path('', include(router.urls)),
]