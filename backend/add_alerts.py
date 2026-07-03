import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uav_backend.settings')
django.setup()

from apps.inspection.models import Alert, InspectionTask
import random
from datetime import datetime, timedelta


task = InspectionTask.objects.first()
if not task:
    print("❌ 没有找到任何巡检任务，请先运行 python manage.py seed_demo 生成任务。")
else:
    
    for i in range(5):
        Alert.objects.create(
            task=task,
            route_name=f"航线-{i+1}",
            alert_time=datetime.now() - timedelta(days=random.randint(0, 3), hours=random.randint(0, 23)),
            detect_type=random.choice(['obstacle', 'defect', 'anomaly', 'other']),
            description=f"测试告警描述 {i+1}",
            location=f"位置 {i+1}",
            status=random.choice(['pending', 'processing', 'resolved', 'ignored']),
        )
    print("✅ 成功创建 5 条告警记录！")