from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True


class Device(TimeStampedModel):
    STATUS_CHOICES = [
        ("online", "在线"),
        ("offline", "离线"),
        ("maintenance", "维护中"),
    ]

    code = models.CharField(max_length=64, unique=True, verbose_name="设备编号")
    name = models.CharField(max_length=100, verbose_name="设备名称")
    model = models.CharField(max_length=100, blank=True, verbose_name="设备型号")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="offline",
        verbose_name="设备状态",
    )
    battery_level = models.PositiveSmallIntegerField(default=100, verbose_name="电量")
    location = models.CharField(max_length=200, blank=True, verbose_name="当前位置")
    last_online_at = models.DateTimeField(null=True, blank=True, verbose_name="最后在线时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "设备"
        verbose_name_plural = "设备"

    def __str__(self):
        return f"{self.code} - {self.name}"


class InspectionTask(TimeStampedModel):
    STATUS_CHOICES = [
        ("pending", "待执行"),
        ("running", "执行中"),
        ("completed", "已完成"),
        ("cancelled", "已取消"),
    ]

    PRIORITY_CHOICES = [
        ("low", "低"),
        ("medium", "中"),
        ("high", "高"),
    ]

    name = models.CharField(max_length=120, verbose_name="任务名称")
    device = models.ForeignKey(
        Device,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="inspection_tasks",
        verbose_name="执行设备",
    )
    area = models.CharField(max_length=120, blank=True, verbose_name="巡检区域")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="任务状态",
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="medium",
        verbose_name="优先级",
    )
    progress = models.PositiveSmallIntegerField(default=0, verbose_name="进度")
    planned_start_at = models.DateTimeField(null=True, blank=True, verbose_name="计划开始时间")
    planned_end_at = models.DateTimeField(null=True, blank=True, verbose_name="计划结束时间")
    description = models.TextField(blank=True, verbose_name="任务描述")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "巡检任务"
        verbose_name_plural = "巡检任务"

    def __str__(self):
        return self.name
