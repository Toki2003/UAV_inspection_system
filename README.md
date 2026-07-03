# UAV 无人机巡检系统

这是一个前后端分离的无人机巡检管理系统框架。

- 前端：Vue 3 + Vite + Pinia + Element Plus + Axios
- 后端：Python + Django + Django REST Framework
- 默认数据库：SQLite，便于本地开发；后续可切换 MySQL/PostgreSQL

## 项目结构

```text
UAV_inspection_system/
├─ frontend/                  # Vue 3 前端
│  ├─ src/
│  │  ├─ api/                 # Axios 请求封装
│  │  ├─ router/              # Vue Router
│  │  ├─ store/               # Pinia
│  │  └─ views/               # 页面
│  ├─ package.json
│  └─ vite.config.js
└─ backend/                   # Django 后端
   ├─ apps/inspection/        # 巡检业务 app
   │  ├─ models.py            # Device、InspectionTask
   │  ├─ serializers.py       # DRF 序列化
   │  ├─ views.py             # API 视图
   │  └─ urls.py              # 业务路由
   ├─ uav_backend/            # Django 项目配置
   ├─ manage.py
   ├─ requirements.txt
   └─ .env.example
```

## 快速启动

### 后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo   # 可选：生成演示设备和任务
python manage.py runserver 0.0.0.0:8080
```

也可以在 Windows 下直接运行：

```bash
cd backend
run.bat
```

后端地址：`http://localhost:8080`

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端地址：`http://localhost:5173`

Vite 已将 `/api` 代理到 `http://localhost:8080`。

## 核心 API

统一响应格式：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```

### 系统概览

| 方法 | 地址 | 说明 |
| --- | --- | --- |
| GET | `/api/health/` | 健康检查 |
| GET | `/api/overview/` | 系统统计概览 |

### 巡检任务

| 方法 | 地址 | 说明 |
| --- | --- | --- |
| GET | `/api/inspection/list` | 获取任务列表 |
| GET | `/api/inspection/{id}` | 获取任务详情 |
| POST | `/api/inspection/create` | 创建任务 |
| PUT | `/api/inspection/{id}` | 更新任务 |
| DELETE | `/api/inspection/{id}` | 删除任务 |
| GET | `/api/inspection/device/{deviceId}` | 按设备查询任务 |
| GET | `/api/inspection/status/{status}` | 按状态查询任务 |

### 设备管理

| 方法 | 地址 | 说明 |
| --- | --- | --- |
| GET | `/api/device/list` | 获取设备列表 |
| GET | `/api/device/{id}` | 获取设备详情 |
| GET | `/api/device/code/{code}` | 按设备编号查询 |
| POST | `/api/device/create` | 创建设备 |
| PUT | `/api/device/{id}` | 更新设备 |
| DELETE | `/api/device/{id}` | 删除设备 |
| GET | `/api/device/online` | 获取在线设备 |
| GET | `/api/device/online/count` | 获取在线设备数量 |

## 数据模型

### Device

- `code`：设备编号，唯一
- `name`：设备名称
- `model`：设备型号
- `status`：`online`、`offline`、`maintenance`
- `battery_level`：电量
- `location`：当前位置
- `last_online_at`：最后在线时间

### InspectionTask

- `name`：任务名称
- `device`：关联设备
- `area`：巡检区域
- `status`：`pending`、`running`、`completed`、`cancelled`
- `priority`：`low`、`medium`、`high`
- `progress`：任务进度
- `planned_start_at`、`planned_end_at`：计划时间
- `description`：任务描述

## 开发说明

- 新增后端接口：在 `backend/apps/inspection/views.py` 编写视图，并在 `urls.py` 注册路由。
- 新增前端接口：在 `frontend/src/api/inspection.js` 统一封装。
- 默认开发配置在 `backend/.env.example`，复制为 `.env` 后可自定义密钥、跨域和数据库配置。
- 如需演示数据，执行 `python manage.py seed_demo`。
