"""
权限管理模块 - 序列化器

处理角色、用户的数据序列化。
用户序列化器处理密码加密和角色关联。
"""

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Role, SysUser


class RoleSerializer(serializers.ModelSerializer):
    """
    角色序列化器

    permissions: 权限码列表，如 ['system:view', 'role:create']
    """

    class Meta:
        model = Role
        fields = ['id', 'name', 'desc', 'permissions', 'create_time']


class SysUserSerializer(serializers.ModelSerializer):
    """
    用户序列化器

    role_name: 只读，返回角色名称用于前端表格展示
    role_id: 写入用，前端传入角色 ID 分配/修改角色
    password: 写入用，自动加密存储，接口不返回密码字段

    设计说明：
    - 角色分配统一通过 role_id 字段完成（新建用户 / 修改用户均可）
    - role 字段设为只读，避免前端误传角色对象导致创建新角色
    """

    # 只读：返回角色名称，用于前端列表展示。角色未分配时返回空字符串
    role_name = serializers.SerializerMethodField()
    # 只读：返回角色对象详情，供前端展示角色完整信息
    role = serializers.SerializerMethodField()
    # 写入用：前端传入角色 ID 进行角色分配或修改
    role_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    # 写入用：密码自动加密，接口不返回
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = SysUser
        fields = [
            'id', 'username', 'real_name', 'role', 'role_id',
            'role_name', 'phone', 'password', 'is_active', 'create_time'
        ]

    def get_role_name(self, obj):
        """返回角色名称，角色未分配时返回空字符串"""
        if obj.role:
            return obj.role.name
        return ''

    def get_role(self, obj):
        """返回角色详情，角色未分配时返回 null"""
        if obj.role:
            return RoleSerializer(obj.role).data
        return None

    def create(self, validated_data):
        """
        新建用户，自动加密明文密码

        role_id 由 DRF 放入 validated_data，Django 模型直接接受 role_id 设置外键。
        """
        if validated_data.get('password'):
            validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        编辑用户信息，支持修改角色

        - 密码非空时重新加密
        - role_id 存在时更新角色关联
        """
        new_pwd = validated_data.get('password')
        if new_pwd:
            validated_data['password'] = make_password(new_pwd)
        return super().update(instance, validated_data)
