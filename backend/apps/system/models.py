"""
权限管理模块 - 数据模型

RBAC 权限体系：用户 -> 角色
- Role: 角色，用户通过关联角色获得权限
- SysUser: 系统用户，继承 Django AbstractUser
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    """
    角色模型

    用户通过 role 外键关联角色，实现基于角色的权限控制。
    """

    name = models.CharField(max_length=32, unique=True, verbose_name='角色名称')
    desc = models.CharField(max_length=128, blank=True, verbose_name='角色说明')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

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