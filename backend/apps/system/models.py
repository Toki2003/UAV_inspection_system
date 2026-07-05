"""
权限管理模块 - 数据模型

本模块实现 RBAC（基于角色的访问控制）体系的核心数据层：
  SysUser --ForeignKey--> Role --JSONField--> permissions[]

设计约束：
  1. 权限以字符串权限码形式存储在 Role.permissions（JSON 数组），如 ["role:view", "user:create"]
  2. 用户通过外键关联角色获得权限，不支持多角色叠加
  3. super_admin 角色的权限由代码层 ALL_PERMISSIONS 强制覆盖，不受数据库配置影响
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
import json


class Role(models.Model):
    """
    角色模型

    权限存储采用 JSONField 而非关联表，原因：
      - 权限码为扁平字符串列表，无需额外查询关联表
      - 角色数量少（通常 < 50），JSON 字段读写性能足够
      - 简化部署，无需额外迁移中间表

    基础角色（super_admin / admin / user）由系统初始化创建，不可删除。
    """

    name = models.CharField(max_length=32, unique=True, verbose_name='角色名称')
    desc = models.CharField(max_length=128, blank=True, verbose_name='角色说明')
    permissions = models.JSONField(default=list, blank=True, verbose_name='权限码列表')
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

    继承 AbstractUser 以复用 Django 内置认证体系（密码哈希、权限检查、Session 等）。
    通过 role 外键关联角色获得 RBAC 权限；role 为可空外键，未分配角色时用户仅有隐式个人权限。
    on_delete=SET_NULL：角色被删除时用户不被级联删除，仅解绑角色关联。
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

    # 覆盖 Django 原生多对多权限字段，避免与自定义 RBAC 体系的 related_name 冲突
    # 本系统不使用 Django 内置 Group/Permission 机制，统一走 Role.permissions JSON 字段
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