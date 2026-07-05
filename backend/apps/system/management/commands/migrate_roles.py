"""
管理命令：迁移角色数据
将旧 admin 角色重命名为 super_admin，并创建基础角色
"""
from django.core.management.base import BaseCommand
from apps.system.models import Role, SysUser


ADMIN_DEFAULT_PERMISSIONS = [
    'user:view', 'user:create', 'user:update',
    'role:view', 'role:assign',
    'alert:view', 'alert:handle',
    'drone:view', 'drone:control',
]


class Command(BaseCommand):
    help = '将旧 admin 角色重命名为 super_admin，并创建基础角色'

    def handle(self, *args, **options):
        self.stdout.write('=== 开始角色迁移 ===\n')

        # 1. 创建或获取 super_admin 角色
        super_admin_role, created = Role.objects.get_or_create(
            name='super_admin',
            defaults={'desc': '超级管理员，拥有系统所有权限（唯一）'}
        )
        if created:
            self.stdout.write('[+] 创建角色 super_admin')
        else:
            self.stdout.write('[=] 角色 super_admin 已存在')

        # 2. 处理旧的 admin 角色
        old_admin = Role.objects.filter(name='admin').first()
        if old_admin:
            SysUser.objects.filter(role=old_admin).update(role=super_admin_role)
            old_admin.delete()
            self.stdout.write('[>] 旧 admin 角色已删除，用户已迁移到 super_admin')
        else:
            self.stdout.write('[=] 无旧 admin 角色需要迁移')

        # 3. 创建 admin 角色（普通管理员）
        admin_role, created = Role.objects.get_or_create(
            name='admin',
            defaults={
                'desc': '普通管理员，拥有用户管理、角色分配、业务管理权限',
                'permissions': ADMIN_DEFAULT_PERMISSIONS,
            }
        )
        if created:
            self.stdout.write('[+] 创建角色 admin（普通管理员）')
        else:
            self.stdout.write('[=] 角色 admin 已存在')

        # 4. 创建 user 角色
        user_role, created = Role.objects.get_or_create(
            name='user',
            defaults={'desc': '普通用户，可使用系统功能和查看自己的数据'}
        )
        if created:
            self.stdout.write('[+] 创建角色 user')
        else:
            self.stdout.write('[=] 角色 user 已存在')

        # 5. 确保 admin 用户关联 super_admin
        admin_user = SysUser.objects.filter(username='admin').first()
        if admin_user:
            if admin_user.role != super_admin_role:
                admin_user.role = super_admin_role
                admin_user.save()
                self.stdout.write('[>] admin 用户角色已更新为 super_admin')
            else:
                self.stdout.write('[=] admin 用户已是 super_admin')

        # 6. 创建 manager 用户（普通管理员示例）
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
            self.stdout.write('[+] 创建普通管理员: manager / manager123')
        else:
            self.stdout.write('[=] manager 用户已存在')

        # 7. 创建 testuser 用户（普通用户示例）
        if not SysUser.objects.filter(username='testuser').exists():
            SysUser.objects.create_user(
                username='testuser',
                password='user123',
                real_name='普通用户',
                phone='13800000003',
                email='user@uav.com',
                role=user_role,
                is_staff=False,
            )
            self.stdout.write('[+] 创建普通用户: testuser / user123')
        else:
            self.stdout.write('[=] testuser 用户已存在')

        self.stdout.write('\n=== 迁移完成 ===')
        self.stdout.write('\n角色列表：')
        for role in Role.objects.all():
            user_count = SysUser.objects.filter(role=role).count()
            self.stdout.write(f'  - {role.name}: {role.desc} ({user_count} 个用户)')
