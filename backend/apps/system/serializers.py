"""
权限管理模块 - 序列化器

职责：
  - RoleSerializer：角色 CRUD 的数据序列化，直接映射 Model 字段
  - SysUserSerializer：用户 CRUD 的数据序列化，处理密码加密、角色关联的读写分离

设计决策：
  用户角色分配统一通过 role_id（写入字段）完成，
  role / role_name 为只读计算字段，仅用于响应中返回角色信息，
  避免前端误传角色对象导致创建新角色。
"""

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Role, SysUser


class RoleSerializer(serializers.ModelSerializer):
    """
    角色序列化器

    permissions 字段为 JSONField，DRF 自动序列化为 JSON 数组。
    前端提交权限码列表如 ["role:view", "user:create"]，直接存入数据库。
    """

    class Meta:
        model = Role
        fields = ['id', 'name', 'desc', 'permissions', 'create_time']


class SysUserSerializer(serializers.ModelSerializer):
    """
    用户序列化器

    字段读写分离设计：
      - role_id (write_only)：前端传入角色 ID 进行角色分配，DRF 自动将 ID 映射为外键
      - role / role_name (read_only)：响应中返回角色详情和角色名，供前端展示
      - password (write_only)：写入时自动加密，响应中永不返回密码字段

    角色未分配时：role 返回 null，role_name 返回空字符串
    """

    role_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    role_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = SysUser
        fields = [
            'id', 'username', 'real_name', 'role', 'role_id',
            'role_name', 'phone', 'password', 'is_active', 'create_time'
        ]

    def get_role_name(self, obj):
        """返回角色名称，用于前端表格列展示；角色未分配时返回空字符串"""
        if obj.role:
            return obj.role.name
        return ''

    def get_role(self, obj):
        """返回嵌套的角色对象详情（id/name/desc/permissions），供前端编辑弹窗使用"""
        if obj.role:
            return RoleSerializer(obj.role).data
        return None

    def create(self, validated_data):
        """
        新建用户时自动加密密码

        role_id 由 DRF 自动映射为 Role 外键，无需额外处理。
        """
        if validated_data.get('password'):
            validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        编辑用户信息，密码非空时重新加密

        role_id 存在时更新外键关联；未传 role_id 时保持原角色不变。
        """
        new_pwd = validated_data.get('password')
        if new_pwd:
            validated_data['password'] = make_password(new_pwd)
        return super().update(instance, validated_data)
