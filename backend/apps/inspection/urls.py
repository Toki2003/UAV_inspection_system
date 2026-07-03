from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'alert', views.AlertViewSet, basename='alert')


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
    path('', include(router.urls)),
]
