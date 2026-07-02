from django.core.management.base import BaseCommand

from apps.inspection.models import Device, InspectionTask


class Command(BaseCommand):
    help = "Create demo devices and inspection tasks for local development."

    def handle(self, *args, **options):
        devices = [
            {
                "code": "UAV-001",
                "name": "巡检一号",
                "model": "DJI M350 RTK",
                "status": "online",
                "battery_level": 88,
                "location": "A 区机库",
            },
            {
                "code": "UAV-002",
                "name": "巡检二号",
                "model": "DJI M30T",
                "status": "online",
                "battery_level": 76,
                "location": "B 区临时起降点",
            },
            {
                "code": "UAV-003",
                "name": "巡检三号",
                "model": "Autel EVO Max",
                "status": "maintenance",
                "battery_level": 42,
                "location": "维修库",
            },
        ]

        device_objects = {}
        for item in devices:
            device, _ = Device.objects.update_or_create(
                code=item["code"],
                defaults=item,
            )
            device_objects[item["code"]] = device

        tasks = [
            {
                "name": "电力线路巡检",
                "device": device_objects["UAV-001"],
                "area": "A 区",
                "status": "running",
                "priority": "high",
                "progress": 65,
                "description": "检查主干输电线路和杆塔状态。",
            },
            {
                "name": "建筑外立面检测",
                "device": device_objects["UAV-002"],
                "area": "B 区",
                "status": "completed",
                "priority": "medium",
                "progress": 100,
                "description": "采集楼体外立面照片并标记异常点。",
            },
            {
                "name": "农田长势监测",
                "device": device_objects["UAV-001"],
                "area": "C 区",
                "status": "pending",
                "priority": "low",
                "progress": 0,
                "description": "规划航线并采集多光谱影像。",
            },
        ]

        for item in tasks:
            InspectionTask.objects.update_or_create(
                name=item["name"],
                defaults=item,
            )

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
