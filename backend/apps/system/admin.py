from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Menu, Role, SysUser


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    """后台菜单管理页面配置"""
    list_display = ['id', 'title', 'path', 'parent', 'sort', 'is_show']
    # 列表页可直接修改排序、显示状态
    list_editable = ['sort', 'is_show']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """后台角色管理页面配置"""
    list_display = ['id', 'name', 'desc']
    # 多对多菜单使用横向多选框，操作更直观
    filter_horizontal = ['menus']


@admin.register(SysUser)
class SysUserAdmin(UserAdmin):
    """后台用户管理页面，继承原生用户管理，扩展自定义字段"""
    list_display = ['id', 'username', 'real_name', 'role', 'phone', 'is_active', 'create_time']
    # 在原有用户编辑页新增扩展信息分组
    fieldsets = UserAdmin.fieldsets + (
        ('业务扩展信息', {'fields': ('real_name', 'role', 'phone')}),
    )