from django.contrib import admin

from .models import Device, InspectionTask


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "model", "status", "battery_level", "updated_at")
    list_filter = ("status",)
    search_fields = ("code", "name", "model")


@admin.register(InspectionTask)
class InspectionTaskAdmin(admin.ModelAdmin):
    list_display = ("name", "device", "area", "status", "priority", "progress", "updated_at")
    list_filter = ("status", "priority")
    search_fields = ("name", "area", "description")
