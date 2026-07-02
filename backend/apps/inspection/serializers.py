from rest_framework import serializers

from .models import Device, InspectionTask


class DeviceSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Device
        fields = [
            "id",
            "code",
            "name",
            "model",
            "status",
            "status_display",
            "battery_level",
            "location",
            "last_online_at",
            "created_at",
            "updated_at",
        ]


class InspectionTaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    device_name = serializers.CharField(source="device.name", read_only=True)

    class Meta:
        model = InspectionTask
        fields = [
            "id",
            "name",
            "device",
            "device_name",
            "area",
            "status",
            "status_display",
            "priority",
            "priority_display",
            "progress",
            "planned_start_at",
            "planned_end_at",
            "description",
            "created_at",
            "updated_at",
        ]
