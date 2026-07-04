from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Role, SysUser


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """后台角色管理页面配置"""
    list_display = ['id', 'name', 'desc']


@admin.register(SysUser)
class SysUserAdmin(UserAdmin):
    """后台用户管理页面，继承原生用户管理，扩展自定义字段"""
    list_display = ['id', 'username', 'real_name', 'role', 'phone', 'is_active', 'create_time']
    # 在原有用户编辑页新增扩展信息分组
    fieldsets = UserAdmin.fieldsets + (
        ('业务扩展信息', {'fields': ('real_name', 'role', 'phone')}),
    )
