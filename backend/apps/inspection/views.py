from django.db.models import Count, Q
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404

from .models import Device, InspectionTask
from .responses import fail, success
from .serializers import (
    DeviceSerializer, 
    InspectionTaskSerializer,
    DroneCommandSerializer,
)
from .services.drone_control import (
    get_telemetry,
    send_command,
    get_video,
    get_dock_overview,
    get_dock_list,
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


# ── 登录认证（预留接口，当前使用 mock 数据） ──────────────────────

import hashlib
import time

# Mock 用户数据 —— 以后接入真实数据库时替换为 User 模型查询
MOCK_USERS = {
    "admin": {
        "id": 1,
        "username": "admin",
        "password": "admin123",
        "nickname": "系统管理员",
        "email": "admin@uav.com",
        "phone": "13800000000",
        "role": "admin",
    },
    "user": {
        "id": 2,
        "username": "user",
        "password": "user123",
        "nickname": "普通用户",
        "email": "user@uav.com",
        "phone": "13800000001",
        "role": "user",
    },
}


@api_view(["POST"])
def login(request):
    """用户登录 —— POST /api/auth/login"""
    username = (request.data.get("username") or "").strip()
    password = (request.data.get("password") or "").strip()

    if not username:
        return fail("用户名不能为空")
    if not password:
        return fail("密码不能为空")

    user = MOCK_USERS.get(username)
    if not user or user["password"] != password:
        return fail("用户名或密码错误")

    # 生成简单 token（生产环境应使用 JWT）
    token = "tk_" + hashlib.md5(
        f"{user['id']}_{username}_{time.time()}".encode()
    ).hexdigest()

    user_info = {k: v for k, v in user.items() if k != "password"}

    # 记录 token → 用户映射（mock，生产环境用 JWT 解析）
    _TOKEN_STORE[token] = user_info

    return success("登录成功", {"token": token, "user": user_info})


@api_view(["POST"])
def logout(request):
    """用户登出 —— POST /api/auth/logout"""
    token = _get_token(request)
    if token:
        _TOKEN_STORE.pop(token, None)
    return success("退出成功")


@api_view(["GET"])
def userinfo(request):
    """获取当前登录用户信息 —— GET /api/auth/userinfo"""
    token = _get_token(request)
    user_info = _TOKEN_STORE.get(token)
    if not user_info:
        return fail("请先登录", code=401)
    return success("获取用户信息成功", user_info)


# ── 用户管理 CRUD（预留接口，当前使用 mock 数据） ──────────────────

@api_view(["GET"])
def user_list(request):
    """用户列表 —— GET /api/user/list"""
    users = [
        {k: v for k, v in u.items() if k != "password"}
        for u in MOCK_USERS.values()
    ]
    return success("获取用户列表成功", users)


@api_view(["POST"])
def user_create(request):
    """创建用户 —— POST /api/user/create"""
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
    """编辑用户 —— PUT /api/user/<pk>"""
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
    """删除用户 —— DELETE /api/user/<pk>"""
    for uname, u in list(MOCK_USERS.items()):
        if u["id"] == pk:
            del MOCK_USERS[uname]
            return success("删除用户成功")
    return fail("用户不存在")


# ── 告警管理（DRF ViewSet） ──────────────────────────────────────

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Alert
from .serializers import AlertSerializer


class AlertViewSet(viewsets.ModelViewSet):
    """告警管理视图"""
    queryset = Alert.objects.all().order_by('-alert_time')
    serializer_class = AlertSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'detect_type', 'task']
    search_fields = ['description', 'route_name', 'location']
    ordering_fields = ['alert_time', 'status']
    ordering = ['-alert_time']


# ── 内部工具函数 ──────────────────────────────────────────────────

# token → 用户信息映射（mock，生产环境用 JWT）
_TOKEN_STORE = {}


def _get_token(request):
    """从 Authorization 请求头中提取 token"""
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
    try:
        video = get_video(device_code)

        return success(
            "获取无人机视频流信息成功",
            video,
        )
    except ValueError as exc:
        return fail(str(exc))
    except Exception as exc:
        return fail(
            f"获取无人机视频流信息失败：{exc}"
        )    


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