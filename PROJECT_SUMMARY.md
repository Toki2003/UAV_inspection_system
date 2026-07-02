# 项目结构总结

## 当前框架

本项目已调整为前后端分离架构：

- 前端：Vue 3 + Vite + Pinia + Element Plus
- 后端：Django + Django REST Framework
- 通信方式：前端通过 `/api` 代理访问后端

## 前端目录

```text
frontend/
├─ src/
│  ├─ api/
│  │  ├─ request.js
│  │  └─ inspection.js
│  ├─ router/
│  ├─ store/
│  ├─ views/
│  │  ├─ Home.vue
│  │  ├─ Dashboard.vue
│  │  └─ About.vue
│  ├─ App.vue
│  ├─ main.js
│  └─ style.css
├─ package.json
└─ vite.config.js
```

## 后端目录

```text
backend/
├─ apps/
│  └─ inspection/
│     ├─ admin.py
│     ├─ apps.py
│     ├─ models.py
│     ├─ serializers.py
│     ├─ tests.py
│     ├─ urls.py
│     └─ views.py
├─ uav_backend/
│  ├─ settings.py
│  ├─ urls.py
│  ├─ asgi.py
│  └─ wsgi.py
├─ manage.py
├─ requirements.txt
├─ run.bat
└─ run.sh
```

## 已完成内容

- 移除旧 Spring Boot 后端框架。
- 新建 Django 项目和巡检业务 app。
- 建立设备和巡检任务模型。
- 提供设备、任务、概览、健康检查 API。
- 提供 `seed_demo` 命令生成本地演示数据。
- 配置 CORS 和 DRF。
- 修复前端中文乱码和页面模板错误。
- 前端首页、仪表盘已接入新 API，并保留本地示例数据兜底。

## 启动命令

后端：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 0.0.0.0:8080
```

前端：

```bash
cd frontend
npm install
npm run dev
```

## API 响应格式

```json
{
  "code": 200,
  "message": "获取数据成功",
  "data": {}
}
```
