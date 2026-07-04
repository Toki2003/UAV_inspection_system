from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'alert', views.AlertViewSet, basename='alert')

urlpatterns = [
    path("overview/", views.overview),
    # 设备管理
    path("device/list", views.device_list_create),
    path("device/create", views.device_create),
    path("device/online", views.online_devices),
    path("device/online/count", views.online_device_count),
    path("device/code/<str:code>", views.device_by_code),
    path("device/<int:pk>", views.device_detail),
    # 设备视频流（预留接口）
    path("stream/config", views.stream_config),
    path("stream/device/<int:device_id>", views.device_stream),
    # 设备遥测数据（预留接口，mock 数据）
    path("telemetry/device/<int:device_id>", views.device_telemetry),
    path("telemetry/device/<int:device_id>/history", views.device_telemetry_history),
    # 巡检任务
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
    # 告警管理（DRF Router）
    path('', include(router.urls)),
    #机场监控
    path("drone-control/docks/overview",views.dock_overview,),
    path("drone-control/docks/list",views.dock_list,),
   # 无人机实时管控
    path("drone-control/<str:device_code>/telemetry",views.drone_telemetry),
    path("drone-control/<str:device_code>/video",views.drone_video),
    path("drone-control/<str:device_code>/command",views.drone_command),
]