"""
权限管理模块 - 数据模型

RBAC 权限体系：用户 -> 角色 -> 菜单
- Menu: 系统菜单，支持树形结构
- Role: 角色，绑定菜单实现权限控制
- SysUser: 系统用户，继承 Django AbstractUser
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class Menu(models.Model):
    """
    系统菜单模型

    支持树形结构（parent 自关联），角色绑定菜单实现页面访问控制。
    前端根据菜单数据动态渲染侧边栏导航。
    """

    title = models.CharField(max_length=32, verbose_name='菜单名称')
    path = models.CharField(max_length=128, blank=True, verbose_name='前端路由')
    icon = models.CharField(max_length=64, blank=True, verbose_name='菜单图标')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='父菜单'
    )
    sort = models.IntegerField(default=0, verbose_name='排序权重')
    is_show = models.BooleanField(default=True, verbose_name='是否展示')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '系统菜单'
        verbose_name_plural = verbose_name
        ordering = ['sort']

    def __str__(self):
        return self.title


class Role(models.Model):
    """
    角色模型

    RBAC 权限核心，一个角色可绑定多个菜单（多对多）。
    用户通过关联角色获得对应菜单访问权限。
    """

    name = models.CharField(max_length=32, unique=True, verbose_name='角色名称')
    desc = models.CharField(max_length=128, blank=True, verbose_name='角色说明')
    menus = models.ManyToManyField(
        Menu,
        blank=True,
        related_name='roles',
        verbose_name='权限菜单'
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '角色信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SysUser(AbstractUser):
    """
    系统用户模型

    继承 Django AbstractUser，保留原生认证功能。
    通过 role 外键关联角色，实现基于角色的权限控制。
    需在 settings.py 配置 AUTH_USER_MODEL = "system.SysUser"
    """

    real_name = models.CharField(max_length=32, blank=True, verbose_name='真实姓名')
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='所属角色'
    )
    phone = models.CharField(max_length=11, blank=True, verbose_name='联系电话')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    # 覆盖 AbstractUser 的 groups 和 user_permissions，避免 related_name 冲突
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='用户组',
        blank=True,
        related_name='sysuser_groups',
        related_query_name='sysuser_group',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='用户单独权限',
        blank=True,
        related_name='sysuser_permissions',
        related_query_name='sysuser_permission',
    )

    class Meta:
        verbose_name = '系统用户'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.username