"""
初始化系统基础角色和默认用户

创建三个基础角色：
- super_admin: 超级管理员（系统最高权限，唯一），拥有所有权限，不可删除
- admin: 普通管理员（可配置权限），拥有用户管理、角色分配、业务管理权限
- user: 普通用户，仅可使用系统功能和查看自己的数据
"""

from django.core.management.base import BaseCommand
from apps.system.models import SysUser, Role


# admin 角色的默认权限码（可配置）
ADMIN_DEFAULT_PERMISSIONS = [
    # 用户管理（部分）
    'user:view', 'user:create', 'user:update', 'user:assign_role',
    # 角色分配（有限）
    'role:view', 'role:assign',
    # 业务管理
    'alert:view', 'alert:handle',
    'drone:view', 'drone:control',
]


class Command(BaseCommand):
    help = "初始化系统基础角色和默认用户"

    def handle(self, *args, **options):
        # ── 1. 创建基础角色 ──

        # 超级管理员（系统最高权限，唯一）
        super_admin_role, created = Role.objects.get_or_create(
            name='super_admin',
            defaults={'desc': '超级管理员，拥有系统所有权限（唯一）'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('角色 super_admin 已创建'))
        else:
            self.stdout.write('角色 super_admin 已存在')

        # 普通管理员（可配置权限）
        admin_role, created = Role.objects.get_or_create(
            name='admin',
            defaults={
                'desc': '普通管理员，拥有用户管理、角色分配、业务管理权限',
                'permissions': ADMIN_DEFAULT_PERMISSIONS,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('角色 admin 已创建'))
        else:
            self.stdout.write('角色 admin 已存在')

        # 普通用户（权限永远为空，由代码层控制）
        user_role, created = Role.objects.get_or_create(
            name='user',
            defaults={'desc': '普通用户，可使用系统功能和查看自己的数据', 'permissions': []}
        )
        if not created and user_role.permissions != []:
            user_role.permissions = []
            user_role.save()
            self.stdout.write(self.style.WARNING('角色 user 的权限已重置为空'))
        if created:
            self.stdout.write(self.style.SUCCESS('角色 user 已创建'))
        else:
            self.stdout.write('角色 user 已存在')

        # ── 2. 将已有 admin 用户的角色从旧 admin 迁移到 super_admin ──
        # 兼容旧数据：如果存在 username='admin' 或 'superadmin' 的用户，
        # 将其角色更新为 super_admin
        old_admin_users = SysUser.objects.filter(username__in=['admin', 'superadmin'])
        for u in old_admin_users:
            if u.role and u.role.name != 'super_admin':
                u.role = super_admin_role
                u.save()
                self.stdout.write(self.style.WARNING(
                    f'用户 {u.username} 的角色已迁移到 super_admin'
                ))

        # ── 3. 创建默认用户 ──

        # 超级管理员账号
        if not SysUser.objects.filter(username='superadmin').exists():
            SysUser.objects.create_user(
                username='superadmin',
                password='admin123',
                real_name='超级管理员',
                phone='13800000000',
                email='admin@uav.com',
                role=super_admin_role,
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write(self.style.SUCCESS('创建超级管理员: superadmin / admin123'))
        else:
            admin_user = SysUser.objects.get(username='superadmin')
            if admin_user.role != super_admin_role:
                admin_user.role = super_admin_role
                admin_user.save()
            self.stdout.write('超级管理员账号已存在')

        # 普通管理员账号（可选，示例）
        if not SysUser.objects.filter(username='manager').exists():
            SysUser.objects.create_user(
                username='manager',
                password='manager123',
                real_name='普通管理员',
                phone='13800000002',
                email='manager@uav.com',
                role=admin_role,
                is_staff=True,
            )
            self.stdout.write(self.style.SUCCESS('创建普通管理员: manager / manager123'))
        else:
            self.stdout.write('普通管理员账号已存在')

        # 普通用户
        if not SysUser.objects.filter(username='user').exists():
            SysUser.objects.create_user(
                username='user',
                password='user123',
                real_name='普通用户',
                phone='13800000001',
                email='user@uav.com',
                role=user_role,
            )
            self.stdout.write(self.style.SUCCESS('创建普通用户: user / user123'))
        else:
            normal_user = SysUser.objects.get(username='user')
            if normal_user.role != user_role:
                normal_user.role = user_role
                normal_user.save()
            self.stdout.write('普通用户账号已存在')

        self.stdout.write(self.style.SUCCESS('\n初始化完成！默认账号：'))
        self.stdout.write('  superadmin / admin123    (超级管理员 super_admin)')
        self.stdout.write('  manager    / manager123  (普通管理员 admin)')
        self.stdout.write('  user       / user123     (普通用户 user)')
