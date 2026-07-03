from rest_framework import serializers

from .models import Device, InspectionTask, Alert


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


class AlertSerializer(serializers.ModelSerializer):

    task_name = serializers.CharField(source='task.name', read_only=True, allow_null=True)

    class Meta:
        model = Alert
        fields = '__all__'
        read_only_fields = ['id', 'alert_time']

class DroneCommandSerializer(serializers.Serializer):
   COMMAND_CHOICES=[
    ("RETURN_HOME", "返航"),
        ("CANCEL_RETURN_HOME", "取消返航"),
        ("PAUSE", "暂停"),
        ("RESUME", "恢复"),
        ("START_INSPECTION", "开始检测"),
    ]   
   command=serializers.ChoiceField(
       choices=COMMAND_CHOICES, 
        required=True, 
        error_messages={
            "required": "命令不能为空", 
            "invalid_choice": "无效的命令"},
)    
