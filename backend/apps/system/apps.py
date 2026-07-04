from django.apps import AppConfig


class SystemConfig(AppConfig):
    # 数据库表前缀
    default_auto_field = 'django.db.models.BigAutoField'
    # 应用注册名称，settings中注册填写此字符串
    name = 'apps.system'
    # admin后台展示名称
    verbose_name = '系统权限管理'