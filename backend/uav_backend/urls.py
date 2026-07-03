from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view

from apps.inspection.responses import success


@api_view(["GET"])
def health_check(request):
    return success("服务运行正常", {"service": "uav-inspection-backend"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check),
    path("api/", include("apps.inspection.urls")),
]
