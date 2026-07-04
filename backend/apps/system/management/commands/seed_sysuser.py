"""
初始化默认角色和用户

创建 admin 和 user 两个角色，以及对应的默认用户。
"""

from django.core.management.base import BaseCommand
from apps.system.models import SysUser, Role


class Command(BaseCommand):
    help = "初始化默认角色和用户"

    def handle(self, *args, **options):
        # ── 1. 创建角色 ──
        admin_role, _ = Role.objects.get_or_create(
            name='admin',
            defaults={'desc': '超级管理员，拥有所有权限'}
        )
        self.stdout.write(self.style.SUCCESS('Admin role created'))

        user_role, _ = Role.objects.get_or_create(
            name='user',
            defaults={'desc': '普通用户'}
        )
        self.stdout.write(self.style.SUCCESS('User role created'))

        # ── 2. 创建用户 ──
        if not SysUser.objects.filter(username='admin').exists():
            SysUser.objects.create_user(
                username='admin',
                password='admin123',
                real_name='系统管理员',
                phone='13800000000',
                email='admin@uav.com',
                role=admin_role,
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write(self.style.SUCCESS('Created admin user: admin / admin123'))
        else:
            admin_user = SysUser.objects.get(username='admin')
            admin_user.role = admin_role
            admin_user.save()
            self.stdout.write('Admin user already exists, role updated')

        if not SysUser.objects.filter(username='user').exists():
            SysUser.objects.create_user(
                username='user',
                password='user123',
                real_name='普通用户',
                phone='13800000001',
                email='user@uav.com',
                role=user_role,
            )
            self.stdout.write(self.style.SUCCESS('Created user: user / user123'))
        else:
            normal_user = SysUser.objects.get(username='user')
            normal_user.role = user_role
            normal_user.save()
            self.stdout.write('User already exists, role updated')

        self.stdout.write(self.style.SUCCESS('\nDone! Default accounts:'))
        self.stdout.write('  admin / admin123 (超级管理员)')
        self.stdout.write('  user  / user123  (普通用户)')
