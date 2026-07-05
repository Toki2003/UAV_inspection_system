import hashlib
import random
import time

from django.conf import settings
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404

from .models import Device, InspectionTask, Alert
from .responses import fail, success
from .serializers import (
    DeviceSerializer,
    InspectionTaskSerializer,
    AlertSerializer,
    DroneCommandSerializer,
)

from .services.drone_control import (
    get_telemetry,
    send_command,
    get_video,
    get_dock_overview,
    get_dock_list,
    get_safety_status,
    get_alert_status,
    request_takeover,
    get_emqx_status,
    subscribe_emqx,
)


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


@api_view(["POST"])
def login(request):
    username = (request.data.get("username") or "").strip()
    password = (request.data.get("password") or "").strip()

    if not username:
        return fail("用户名不能为空")
    if not password:
        return fail("密码不能为空")

    user = MOCK_USERS.get(username)
    if not user or user["password"] != password:
        return fail("用户名或密码错误")

    token = "tk_" + hashlib.md5(
        f"{user['id']}_{username}_{time.time()}".encode()
    ).hexdigest()

    user_info = {k: v for k, v in user.items() if k != "password"}
    _TOKEN_STORE[token] = user_info

    return success("登录成功", {"token": token, "user": user_info})


@api_view(["POST"])
def logout(request):
    token = _get_token(request)
    if token:
        _TOKEN_STORE.pop(token, None)
    return success("退出成功")


@api_view(["GET"])
def userinfo(request):
    token = _get_token(request)
    user_info = _TOKEN_STORE.get(token)
    if not user_info:
        return fail("请先登录", code=401)
    return success("获取用户信息成功", user_info)


@api_view(["GET"])
def user_list(request):
    users = [
        {k: v for k, v in u.items() if k != "password"}
        for u in MOCK_USERS.values()
    ]
    return success("获取用户列表成功", users)


@api_view(["POST"])
def user_create(request):
    username = (request.data.get("username") or "").strip()
    if not username:
        return fail("用户名不能为空")
    if username in MOCK_USERS:
        return fail("用户名已存在")

    new_id = max(u["id"] for u in MOCK_USERS.values()) + 1
    MOCK_USERS[username] = {
        "id": new_id,
        "username": username,
        "password": request.data.get("password", "123456"),
        "nickname": request.data.get("nickname", username),
        "email": request.data.get("email", ""),
        "phone": request.data.get("phone", ""),
        "role": request.data.get("role", "user"),
    }
    user_info = {k: v for k, v in MOCK_USERS[username].items() if k != "password"}
    return success("创建用户成功", user_info)


@api_view(["PUT"])
def user_update(request, pk):
    for uname, u in MOCK_USERS.items():
        if u["id"] == pk:
            for field in ("nickname", "email", "phone", "role"):
                if field in request.data:
                    u[field] = request.data[field]
            if "password" in request.data and request.data["password"]:
                u["password"] = request.data["password"]
            user_info = {k: v for k, v in u.items() if k != "password"}
            return success("更新用户成功", user_info)
    return fail("用户不存在")


@api_view(["DELETE"])
def user_delete(request, pk):
    for uname, u in list(MOCK_USERS.items()):
        if u["id"] == pk:
            del MOCK_USERS[uname]
            return success("删除用户成功")
    return fail("用户不存在")


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all().order_by('-alert_time')
    serializer_class = AlertSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'detect_type', 'task']
    search_fields = ['description', 'route_name', 'location']
    ordering_fields = ['alert_time', 'status']
    ordering = ['-alert_time']


# ── 视频流接口（预留，接入真实 RTSP 流时实现） ────────────────────────

@api_view(["GET"])
def stream_config(request):
    """
    获取视频流全局配置

    预留接口，接入真实流媒体服务器后返回实际配置。
    """
    return success("获取视频流配置成功", {
        "enabled": settings.RTSP_ENABLED,
        "mediaServer": settings.RTSP_MEDIA_SERVER,
        "defaultPort": settings.RTSP_DEFAULT_PORT,
        "protocol": "rtsp",
    })


@api_view(["GET"])
def device_stream(request, device_id):
    """
    获取指定设备的视频流信息

    预留接口，接入真实设备后返回实际 RTSP 地址或流媒体代理地址。
    当前返回 mock 数据供前端调试。
    """
    device = get_object_or_404(Device, pk=device_id)

    if not settings.RTSP_ENABLED:
        return success("视频流功能未启用", {
            "deviceId": device.id,
            "deviceCode": device.code,
            "streamAvailable": False,
            "message": "视频流功能未启用，请在 .env 中设置 RTSP_ENABLED=True",
        })

    # mock 数据：接入真实设备后替换为实际流地址
    mock_stream_url = device.rtsp_url or f"rtsp://mock-device-{device.id}:554/stream1"
    mock_hls_url = f"{settings.RTSP_MEDIA_SERVER}/live/{device.code}.m3u8"

    return success("获取设备视频流成功", {
        "deviceId": device.id,
        "deviceCode": device.code,
        "streamAvailable": device.stream_enabled,
        "rtspUrl": mock_stream_url,
        "hlsUrl": mock_hls_url,
        "status": "online" if device.status == "online" else "offline",
    })


# ── 设备遥测数据接口（预留，接入真实设备时实现） ──────────────────────

@api_view(["GET"])
def device_telemetry(request, device_id):
    """
    获取设备实时遥测数据

    预留接口，接入真实设备后返回实际传感器数据。
    当前返回 mock 数据供前端调试。
    """
    device = get_object_or_404(Device, pk=device_id)

    # mock 遥测数据：接入真实设备后替换为实际数据源
    mock_telemetry = {
        "deviceId": device.id,
        "deviceCode": device.code,
        "timestamp": int(time.time() * 1000),
        "gps": {
            "latitude": 23.1291 + random.uniform(-0.001, 0.001),
            "longitude": 113.2644 + random.uniform(-0.001, 0.001),
            "altitude": 50 + random.uniform(-5, 20),
        },
        "battery": {
            "level": device.battery_level,
            "voltage": round(3.7 + device.battery_level * 0.005, 2),
            "charging": False,
        },
        "flight": {
            "speed": round(random.uniform(0, 15), 1),
            "heading": round(random.uniform(0, 360), 1),
            "verticalSpeed": round(random.uniform(-2, 3), 1),
        },
        "signal": {
            "gps": random.randint(8, 14),
            "rc": random.randint(-80, -40),
            "video": random.randint(-70, -30),
        },
        "environment": {
            "windSpeed": round(random.uniform(0, 8), 1),
            "temperature": round(random.uniform(15, 35), 1),
            "humidity": random.randint(40, 80),
        },
    }

    return success("获取设备遥测数据成功", mock_telemetry)


@api_view(["GET"])
def device_telemetry_history(request, device_id):
    """
    获取设备历史遥测数据

    预留接口，接入真实设备后从数据库/时序数据库查询。
    当前返回 mock 数据供前端调试。
    """
    device = get_object_or_404(Device, pk=device_id)

    # mock 历史数据：生成最近 10 条记录
    now = int(time.time() * 1000)
    mock_history = [
        {
            "timestamp": now - i * 5000,
            "gps": {
                "latitude": 23.1291 + random.uniform(-0.002, 0.002),
                "longitude": 113.2644 + random.uniform(-0.002, 0.002),
                "altitude": 50 + random.uniform(-5, 30),
            },
            "battery": device.battery_level - i,
            "speed": round(random.uniform(0, 15), 1),
        }
        for i in range(10)
    ]

    return success("获取历史遥测数据成功", {
        "deviceId": device.id,
        "deviceCode": device.code,
        "records": mock_history,
    })


def _get_token(request):
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return auth

#--无人机实时管控——————————————————————————————————————————————————
@api_view(["GET"])
def drone_telemetry(request,device_code):
    try:
        telemetry = get_telemetry(device_code)
        return success("获取无人机遥测数据成功", telemetry,)
    except ValueError as exc:
        return fail(str(exc))
    except Exception as exc:
        return fail(f"获取无人机遥测数据失败: {str(exc)}")

@api_view(["GET"])
def drone_video(request, device_code):
    stream_type = request.query_params.get(
        "streamType",
        "uav",
    )
    try:
        video = get_video(
            device_code,
            stream_type,
        )
        return success(
            "获取视频流信息成功",
            video,
        )
    except ValueError as exc:
        return fail(str(exc))
    except Exception:
        return fail("获取视频流信息失败")


@api_view(["POST"])
def drone_command(request, device_code):
    serializer = DroneCommandSerializer(
        data=request.data
    )

    if not serializer.is_valid():
        return fail(
            "控制命令参数错误",
            data=serializer.errors,
        )

    command = serializer.validated_data["command"]

    try:
        result = send_command(
            device_code,
            command,
        )

        return success(
            "无人机控制命令发送成功",
            result,
        )
    except ValueError as exc:
        return fail(str(exc))
    except Exception as exc:
        return fail(
            f"发送无人机控制命令失败：{exc}"
        )


@api_view(["GET"])
def drone_safety(request, device_code):
    try:
        return success(
            "获取无人机安全状态成功",
            get_safety_status(device_code),
        )
    except ValueError as exc:
        return fail(str(exc))
    except Exception as exc:
        return fail(f"获取无人机安全状态失败：{exc}")


@api_view(["GET"])
def drone_alert_status(request, device_code):
    try:
        return success(
            "获取无人机预警状态成功",
            get_alert_status(device_code),
        )
    except ValueError as exc:
        return fail(str(exc))
    except Exception as exc:
        return fail(f"获取无人机预警状态失败：{exc}")


@api_view(["POST"])
def drone_takeover(request, device_code):
    try:
        result = request_takeover(device_code)
        return success(result["message"], result)
    except ValueError as exc:
        return fail(str(exc))
    except Exception as exc:
        return fail(f"请求人工接管失败：{exc}")


@api_view(["GET"])
def drone_emqx_status(request, device_code):
    try:
        return success(
            "获取EMQX状态成功",
            get_emqx_status(device_code),
        )
    except ValueError as exc:
        return fail(str(exc))
    except Exception as exc:
        return fail(f"获取EMQX状态失败：{exc}")


@api_view(["POST"])
def drone_emqx_subscribe(request, device_code):
    try:
        result = subscribe_emqx(device_code)
        return success(result["message"], result)
    except ValueError as exc:
        return fail(str(exc))
    except Exception as exc:
        return fail(f"请求EMQX订阅失败：{exc}")

@api_view(["GET"])
def dock_overview(request):
    try:
        overview = get_dock_overview()

        return success(
            "获取机库统计成功",
            overview,
        )
    except Exception:
        return fail("获取机库统计失败")


@api_view(["GET"])
def dock_list(request):
    try:
        docks = get_dock_list()

        return success(
            "获取机库列表成功",
            docks,
        )
    except Exception:
        return fail("获取机库列表失败")
