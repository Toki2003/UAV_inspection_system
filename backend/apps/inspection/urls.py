from django.urls import path

from . import views


urlpatterns = [
    path("overview/", views.overview),
    path("device/list", views.device_list_create),
    path("device/create", views.device_create),
    path("device/online", views.online_devices),
    path("device/online/count", views.online_device_count),
    path("device/code/<str:code>", views.device_by_code),
    path("device/<int:pk>", views.device_detail),
    path("inspection/list", views.inspection_list_create),
    path("inspection/create", views.inspection_create),
    path("inspection/device/<int:device_id>", views.inspection_by_device),
    path("inspection/status/<str:status>", views.inspection_by_status),
    path("inspection/<int:pk>", views.inspection_detail),
    # 登录认证
    path("auth/login", views.login),
    path("auth/logout", views.logout),
    path("auth/userinfo", views.userinfo),
    # 用户管理
    path("user/list", views.user_list),
    path("user/create", views.user_create),
    path("user/<int:pk>", views.user_update),
    path("user/delete/<int:pk>", views.user_delete),
]
