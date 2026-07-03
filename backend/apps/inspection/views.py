from django.db.models import Count, Q
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404

from .models import Device, InspectionTask
from .responses import fail, success
from .serializers import DeviceSerializer, InspectionTaskSerializer

from .models import Device, InspectionTask, Alert
from .serializers import DeviceSerializer, InspectionTaskSerializer, AlertSerializer
@api_view(["GET"])
def overview(request):
    total_tasks = InspectionTask.objects.count()
    completed_tasks = InspectionTask.objects.filter(status="completed").count()
    total_devices = Device.objects.count()
    online_devices = Device.objects.filter(status="online").count()
    active_tasks = InspectionTask.objects.filter(status__in=["pending", "running"]).count()

    task_status = dict(
        InspectionTask.objects.values_list("status").annotate(count=Count("id"))
    )
    device_status = dict(Device.objects.values_list("status").annotate(count=Count("id")))

    return success(
        "获取概览数据成功",
        {
            "totalTasks": total_tasks,
            "completedTasks": completed_tasks,
            "activeTasks": active_tasks,
            "totalDevices": total_devices,
            "onlineDevices": online_devices,
            "taskStatus": task_status,
            "deviceStatus": device_status,
        },
    )


@api_view(["GET", "POST"])
def device_list_create(request):
    if request.method == "GET":
        keyword = request.query_params.get("keyword", "").strip()
        queryset = Device.objects.all()
        if keyword:
            queryset = queryset.filter(Q(name__icontains=keyword) | Q(code__icontains=keyword))
        return success("获取设备列表成功", DeviceSerializer(queryset, many=True).data)

    serializer = DeviceSerializer(data=request.data)
    if serializer.is_valid():
        return success("创建设备成功", DeviceSerializer(serializer.save()).data)
    return fail("创建设备失败", data=serializer.errors)


@api_view(["POST"])
def device_create(request):
    return device_list_create(request)


@api_view(["GET", "PUT", "DELETE"])
def device_detail(request, pk):
    device = get_object_or_404(Device, pk=pk)

    if request.method == "GET":
        return success("获取设备详情成功", DeviceSerializer(device).data)

    if request.method == "PUT":
        serializer = DeviceSerializer(device, data=request.data, partial=True)
        if serializer.is_valid():
            return success("更新设备成功", DeviceSerializer(serializer.save()).data)
        return fail("更新设备失败", data=serializer.errors)

    device.delete()
    return success("删除设备成功", "")


@api_view(["GET"])
def device_by_code(request, code):
    device = get_object_or_404(Device, code=code)
    return success("获取设备成功", DeviceSerializer(device).data)


@api_view(["GET"])
def online_devices(request):
    queryset = Device.objects.filter(status="online")
    return success("获取在线设备成功", DeviceSerializer(queryset, many=True).data)


@api_view(["GET"])
def online_device_count(request):
    return success("获取在线设备数量成功", Device.objects.filter(status="online").count())


@api_view(["GET", "POST"])
def inspection_list_create(request):
    if request.method == "GET":
        queryset = InspectionTask.objects.select_related("device")
        status_value = request.query_params.get("status", "").strip()
        if status_value:
            queryset = queryset.filter(status=status_value)
        return success("获取任务列表成功", InspectionTaskSerializer(queryset, many=True).data)

    serializer = InspectionTaskSerializer(data=request.data)
    if serializer.is_valid():
        return success("创建任务成功", InspectionTaskSerializer(serializer.save()).data)
    return fail("创建任务失败", data=serializer.errors)


@api_view(["POST"])
def inspection_create(request):
    return inspection_list_create(request)


@api_view(["GET", "PUT", "DELETE"])
def inspection_detail(request, pk):
    task = get_object_or_404(InspectionTask.objects.select_related("device"), pk=pk)

    if request.method == "GET":
        return success("获取任务详情成功", InspectionTaskSerializer(task).data)

    if request.method == "PUT":
        serializer = InspectionTaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            return success("更新任务成功", InspectionTaskSerializer(serializer.save()).data)
        return fail("更新任务失败", data=serializer.errors)

    task.delete()
    return success("删除任务成功", "")


@api_view(["GET"])
def inspection_by_device(request, device_id):
    queryset = InspectionTask.objects.filter(device_id=device_id).select_related("device")
    return success("获取设备任务成功", InspectionTaskSerializer(queryset, many=True).data)


@api_view(["GET"])
def inspection_by_status(request, status):
    queryset = InspectionTask.objects.filter(status=status).select_related("device")
    return success("获取任务成功", InspectionTaskSerializer(queryset, many=True).data)
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

class AlertViewSet(viewsets.ModelViewSet):
    """告警管理视图"""
    queryset = Alert.objects.all().order_by('-alert_time')
    serializer_class = AlertSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'detect_type', 'task']   
    search_fields = ['description', 'route_name', 'location']  
    ordering_fields = ['alert_time', 'status']
    ordering = ['-alert_time']  