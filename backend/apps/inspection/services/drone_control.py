from threading import Lock
from typing import Dict
from datetime import datetime

from apps.inspection.models import Device

SUPPORTED_COMMANDS={
    "RETURN_HOME",
    "CANCEL_RETURN_HOME",
    "PAUSE",
    "RESUME",
    "START_INSPECTION",
}

_flight_status_store: Dict[str, str] = {}
_emqx_subscription_store: Dict[str, bool] = {}
_status_lock = Lock()

_VIDEO_STREAM_MOCK = {
    "UAV-001": {
        "airportUrl": "/live/dock01.live.flv",
        "playbackUrl": "/live/uav001.live.flv",
    },
    "UAV-002": {
        "airportUrl": "/live/dock02.live.flv",
        "playbackUrl": "/live/uav002.live.flv",
    },
    "UAV-003": {
        "airportUrl": "/live/dock03.live.flv",
        "playbackUrl": "/live/uav003.live.flv",
    },
}

_DOCK_MOCK_DATA = [
    {
        "dockCode": "DOCK-001",
        "dockName": "A区智能机库",
        "location": "轨道交通A区车辆段",
        "status": "online",
        "alarm": False,
        "temperature": 24.6,
        "humidity": 48.2,
        "windSpeed": 2.3,
        "coverStatus": "closed",
        "droneInDock": True,
        "droneCode": "UAV-001",
        "battery": 88,
        "storageUsage": 42,
        "taskCount": 3,
    },
    {
        "dockCode": "DOCK-002",
        "dockName": "B区智能机库",
        "location": "轨道交通B区停车场",
        "status": "online",
        "alarm": True,
        "temperature": 31.8,
        "humidity": 65.4,
        "windSpeed": 5.6,
        "coverStatus": "open",
        "droneInDock": False,
        "droneCode": "UAV-002",
        "battery": 76,
        "storageUsage": 68,
        "taskCount": 2,
    },
    {
        "dockCode": "DOCK-003",
        "dockName": "维修区机库",
        "location": "轨道交通维修库",
        "status": "offline",
        "alarm": False,
        "temperature": 0.0,
        "humidity": 0.0,
        "windSpeed": 0.0,
        "coverStatus": "unknown",
        "droneInDock": True,
        "droneCode": "UAV-003",
        "battery": 42,
        "storageUsage": 35,
        "taskCount": 0,
    },
]

def get_telemetry(device_code: str) -> dict:
    device = _get_existing_device(device_code)

    return {
        "deviceCode": device.code,
        "deviceName": device.name,
        "deviceModel": device.model,
        "online": device.status == "online",
        "battery": device.battery_level,
        "height": 35.6,
        "speed": 4.2,
        "longitude": 118.796877,
        "latitude": 32.060255,
        "location": device.location,
        "flightStatus": _get_flight_status(device.code),
        "alarmStatus": "正常",
        "updateTime": _current_timestamp_ms(),
        "complianceStatus": "合规",
        "inNoFlyZone": False,
        "encrypted": True,
    }

def send_command(device_code: str, command: str) -> dict:
    device = _get_existing_device(device_code)
    _validate_command(command)
    _update_flight_status(device.code, command)
    return {
        "deviceCode": device.code,
        "command": command,
        "success": True,
        "message": _get_message(command),
        "updateTime": _current_timestamp_ms(),
    }

def get_video(device_code: str, stream_type: str = "uav") -> dict:
    device = _get_existing_device(device_code)
    if stream_type not in {"uav", "airport"}:
        raise ValueError(f"不支持的视频类型：{stream_type}")

    stream_config = _VIDEO_STREAM_MOCK.get(device.code, {})

    if stream_type == "airport":
        video_url = stream_config.get("airportUrl", "")
        stream_name = "机场直播"
    else:
        video_url = stream_config.get("playbackUrl", "")
        stream_name = "无人机直播"

    video_available = bool(
        device.stream_enabled
        and device.rtsp_url
        and video_url
    )

    return {
        "deviceCode": device.code,
        "deviceName": device.name,
        "streamType": stream_type,
        "streamName": stream_name,
        "rtspUrl": device.rtsp_url,
        "videoUrl": video_url,
        "videoProtocol": "FLV",
        "videoAvailable": video_available,
        "mock": True,
    }


def get_safety_status(device_code: str) -> dict:
    device = _get_existing_device(device_code)
    return {
        "deviceCode": device.code,
        "complianceStatus": "合规",
        "inNoFlyZone": False,
        "encrypted": True,
        "systemProtection": "正常",
        "mock": True,
        "reserved": True,
        "updateTime": _current_timestamp_ms(),
    }


def get_alert_status(device_code: str) -> dict:
    device = _get_existing_device(device_code)
    dock = next(
        (
            item
            for item in _DOCK_MOCK_DATA
            if item["droneCode"] == device.code
        ),
        None,
    )
    has_alarm = bool(dock and dock["alarm"])
    return {
        "deviceCode": device.code,
        "activeCount": 1 if has_alarm else 0,
        "level": "warning" if has_alarm else "normal",
        "status": "存在告警" if has_alarm else "正常",
        "message": "机场环境状态异常" if has_alarm else "暂无异常告警",
        "mock": True,
        "reserved": True,
        "updateTime": _current_timestamp_ms(),
    }


def request_takeover(device_code: str) -> dict:
    device = _get_existing_device(device_code)
    return {
        "deviceCode": device.code,
        "accepted": False,
        "available": False,
        "reserved": True,
        "mock": True,
        "message": "人工接管接口已预留，等待真实飞控SDK接入",
        "updateTime": _current_timestamp_ms(),
    }


def get_emqx_status(device_code: str) -> dict:
    device = _get_existing_device(device_code)
    requested = _emqx_subscription_store.get(device.code, False)
    return {
        "deviceCode": device.code,
        "connected": False,
        "brokerConfigured": False,
        "subscriptionRequested": requested,
        "subscriptionStatus": "reserved" if requested else "not_requested",
        "topic": f"uav/{device.code}/telemetry",
        "mock": True,
        "reserved": True,
        "updateTime": _current_timestamp_ms(),
    }


def subscribe_emqx(device_code: str) -> dict:
    device = _get_existing_device(device_code)
    with _status_lock:
        _emqx_subscription_store[device.code] = True
    result = get_emqx_status(device.code)
    result["message"] = "EMQX订阅接口已预留，等待Broker配置"
    return result


def _get_existing_device(device_code: str) -> Device:
    device = Device.objects.filter(code=device_code).first()
    if device is None:
        raise ValueError(f"设备不存在：{device_code}")
    return device


def _validate_command(command: str) -> None:
    if not command:
        raise ValueError("控制命令不能为空")
    if command not in SUPPORTED_COMMANDS:
        raise ValueError(f"不支持的控制命令：{command}")


def _get_flight_status(device_code: str) -> str:
    with _status_lock:
        return _flight_status_store.get(device_code, "巡检中")


def _update_flight_status(device_code: str, command: str) -> None:
    command_status_map = {
        "RETURN_HOME": "返航中",
        "CANCEL_RETURN_HOME": "悬停中",
        "PAUSE": "已暂停",
        "RESUME": "巡检中",
        "START_INSPECTION": "巡检中",
    }
    new_status = command_status_map[command]
    with _status_lock:
        _flight_status_store[device_code] = new_status


def _get_message(command: str) -> str:
    command_message_map = {
        "RETURN_HOME": "返航命令发送成功",
        "CANCEL_RETURN_HOME": "取消返航命令发送成功",
        "PAUSE": "暂停命令发送成功",
        "RESUME": "恢复命令发送成功",
        "START_INSPECTION": "开始巡检命令发送成功",
    }
    return command_message_map[command]

def _current_timestamp_ms() -> int:
    import time

    return int(time.time() * 1000)


def get_dock_overview() -> dict:
    total_count = len(_DOCK_MOCK_DATA)

    online_count = sum(
        1
        for dock in _DOCK_MOCK_DATA
        if dock["status"] == "online"
    )

    offline_count = sum(
        1
        for dock in _DOCK_MOCK_DATA
        if dock["status"] == "offline"
    )

    alarm_count = sum(
        1
        for dock in _DOCK_MOCK_DATA
        if dock["alarm"]
    )

    return {
        "totalCount": total_count,
        "onlineCount": online_count,
        "offlineCount": offline_count,
        "alarmCount": alarm_count,
    }


def get_dock_list() -> list:
    update_time = int(
        datetime.now().timestamp() * 1000
    )

    result = []

    for dock in _DOCK_MOCK_DATA:
        dock_data = dock.copy()
        dock_data["updateTime"] = update_time
        result.append(dock_data)

    return result
