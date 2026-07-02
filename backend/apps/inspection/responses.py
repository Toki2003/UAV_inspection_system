from rest_framework.response import Response


def success(message="操作成功", data=None, code=200):
    return Response({"code": code, "message": message, "data": data})


def fail(message="操作失败", code=400, data=None, http_status=200):
    return Response(
        {"code": code, "message": message, "data": data},
        status=http_status,
    )
