"""
权限管理模块 - 序列化器

处理菜单、角色、用户的数据序列化。
角色序列化器支持通过 menu_ids 绑定菜单权限。
用户序列化器处理密码加密和角色关联。
"""

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Menu, Role, SysUser


class MenuSerializer(serializers.ModelSerializer):
    """菜单序列化，返回全字段"""

    class Meta:
        model = Menu
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    """
    角色序列化器

    menu_ids: 写入用，前端传入菜单 ID 列表绑定权限
    menus: 只读用，返回嵌套菜单数据供前端展示
    """

    # 写入用：前端提交菜单 ID 列表，仅用于创建/更新时绑定权限
    menu_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    # 只读用：返回当前角色绑定的全部菜单嵌套数据
    menus = MenuSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'desc', 'menus', 'menu_ids', 'create_time']

    def create(self, validated_data):
        """新建角色，同时绑定菜单权限"""
        menu_id_list = validated_data.pop('menu_ids', [])
        role_obj = Role.objects.create(**validated_data)
        role_obj.menus.set(menu_id_list)
        return role_obj

    def update(self, instance, validated_data):
        """
        更新角色信息

        menu_ids 存在时重置菜单权限关联，未传则保持原有菜单不变。
        """
        # 仅当前端显式传入 menu_ids 时才更新菜单关联
        update_menus = 'menu_ids' in validated_data
        menu_id_list = validated_data.pop('menu_ids', None)
        for key, val in validated_data.items():
            setattr(instance, key, val)
        instance.save()
        if update_menus:
            instance.menus.set(menu_id_list or [])
        return instance


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

    # 只读：返回角色名称，用于前端列表展示
    role_name = serializers.CharField(source='role.name', read_only=True)
    # 只读：返回角色对象详情，供前端展示角色完整信息
    role = RoleSerializer(read_only=True)
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