# 项目架构总结

## 📋 项目概况

已成功构建一个完整的**前后端分离**的 UAV 无人机巡检系统开发框架:
- **前端**: Vue 3 + Vite + Pinia + Element Plus
- **后端**: Spring Boot 2.7.17 + JDK 1.8 + MySQL + Redis

指 Swagger MVC

---

## 📁 前端项目结构

```
frontend/
├── src/
│   ├── components/          # UI 组件库
│   ├── views/
│   │   ├── Home.vue         # 首页
│   │   ├── Dashboard.vue    # 仪表盘
│   │   └── About.vue        # 关于页面
│   ├── api/
│   │   ├── request.js       # Axios 实例配置
│   │   └── inspection.js    # 巡检 API
│   ├── router/
│   │   └── index.js         # 路由配置
│   ├── store/
│   │   └── index.js         # Pinia 状态管理
│   ├── style.css            # 全局样式
│   ├── App.vue              # 根组件
│   └── main.js              # 入口文件
├── public/                  # 静态资源
├── index.html               # HTML 模板
├── package.json             # 项目依赖
├── vite.config.js           # Vite 配置
├── run.bat                  # Windows 启动脚本
├── run.sh                   # Linux/Mac 启动脚本
└── .gitignore
```

**主要依赖**:
- vue@^3.3.8
- vue-router@^4.2.5
- pinia@^2.1.6
- axios@^1.6.2
- element-plus@^2.4.4
- vite@^5.0.10

**前端命令**:
```bash
npm install      # 安装依赖
npm run dev      # 开发模式（端口 5173）
npm run build    # 生产构建
npm run lint     # 代码检查
```

---

## 📁 后端项目结构

```
backend/
├── src/
│   ├── main/
│   │   ├── java/com/uav/inspection/
│   │   │   ├── controller/
│   │   │   │   ├── InspectionTaskController.java    # 任务控制器
│   │   │   │   └── DeviceController.java            # 设备控制器
│   │   │   ├── service/
│   │   │   │   ├── InspectionTaskService.java       # 任务业务接口
│   │   │   │   ├── DeviceService.java               # 设备业务接口
│   │   │   │   └── impl/                            # 实现类
│   │   │   ├── dao/
│   │   │   │   ├── InspectionTaskRepository.java
│   │   │   │   └── DeviceRepository.java
│   │   │   ├── entity/
│   │   │   │   ├── InspectionTask.java              # 任务实体
│   │   │   │   └── Device.java                      # 设备实体
│   │   │   ├── util/
│   │   │   │   └── ApiResponse.java                 # 统一响应类
│   │   │   └── UavInspectionApplication.java        # 启动类
│   │   └── resources/
│   │       └── application.yml                      # 配置文件
│   └── test/
├── pom.xml                  # Maven 配置
├── run.bat                  # Windows 启动脚本
├── run.sh                   # Linux/Mac 启动脚本
└── .gitignore
```

**主要依赖**:
- spring-boot-starter-web (Spring MVC)
- spring-boot-starter-data-jpa (ORM)
- spring-boot-starter-data-redis (缓存)
- mysql-connector-java@8.0.33 (MySQL 驱动)
- lombok (代码生成)
- fastjson (JSON 处理)

**后端配置** (application.yml):
- 服务器端口: 8080
- 数据库: MySQL (localhost:3306/uav_inspection)
- Redis: localhost:6379
- JPA 自动建表: update

**后端命令**:
```bash
mvn clean compile       # 编译
mvn clean package       # 打包
mvn spring-boot:run     # 运行
```

---

## 🔌 API 接口规范

### 请求/响应格式

所有 API 返回统一格式:
```json
{
  "code": 200,
  "message": "success",
  "data": { ... },
  "timestamp": 1234567890
}
```

### 巡检任务 API

| 方法 | 端点 | 功能 |
|------|------|------|
| GET | `/api/inspection/list` | 获取任务列表 |
| GET | `/api/inspection/{id}` | 获取任务详情 |
| POST | `/api/inspection/create` | 创建任务 |
| PUT | `/api/inspection/{id}` | 更新任务 |
| DELETE | `/api/inspection/{id}` | 删除任务 |
| GET | `/api/inspection/device/{deviceId}` | 按设备查询 |
| GET | `/api/inspection/status/{status}` | 按状态查询 |

### 设备管理 API

| 方法 | 端点 | 功能 |
|------|------|------|
| GET | `/api/device/list` | 获取设备列表 |
| GET | `/api/device/{id}` | 获取设备详情 |
| GET | `/api/device/code/{code}` | 按代码查询 |
| POST | `/api/device/create` | 创建设备 |
| PUT | `/api/device/{id}` | 更新设备 |
| DELETE | `/api/device/{id}` | 删除设备 |
| GET | `/api/device/online` | 获取在线设备 |
| GET | `/api/device/online/count` | 在线设备数量 |

---

## 🎯 功能特性

### 前端
✅ 响应式设计  
✅ 模块化架构  
✅ API 请求拦截器  
✅ 统一的状态管理  
✅ 国际化支持结构（已预留）  

### 后端
✅ 分层架构（MVC）  
✅ ORM 映射（JPA/Hibernate）  
✅ RESTful API 设计  
✅ 统一异常处理  
✅ 数据库自动建表  
✅ 缓存支持（Redis）  

---

## 🚀 快速开始

### 前端启动
```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

### 后端启动
```bash
cd backend
# 修改 application.yml 中的数据库配置
mvn spring-boot:run
# 服务运行在 http://localhost:8080
```

**或使用启动脚本**:
- Windows: 双击 `run.bat`
- Linux/Mac: `bash run.sh`

---

## 📝 数据库初始化

系统会自动在启动时创建数据表。主要表结构：

### inspection_task 表
```sql
- id (主键)
- name (任务名称)
- description (任务描述)
- status (状态: 未开始/进行中/已完成)
- progress (进度百分比)
- device_id (设备 ID)
- area_id (区域 ID)
- created_time (创建时间)
- updated_time (更新时间)
- start_time (开始时间)
- end_time (结束时间)
```

### device 表
```sql
- id (主键)
- code (设备代码)
- name (设备名称)
- type (设备类型)
- status (状态: 在线/离线)
- battery_level (电池电量)
- last_online_time (最后在线时间)
- created_time (创建时间)
- updated_time (更新时间)
```

---

## 📦 项目配置

### 前端代理配置 (vite.config.js)
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8080',
    changeOrigin: true,
  }
}
```

### 跨域配置 (后端)
所有控制器已启用 CORS:
```java
@CrossOrigin(origins = "*", maxAge = 3600)
```

---

## 🛠 开发工具

| 工具 | 用途 |
|------|------|
| VS Code | IDE |
| Git | 版本控制 |
| Maven | 后端构建 |
| npm | 前端包管理 |
| Postman | API 测试 |
| MySQL Workbench | 数据库管理 |

---

## 📚 文档

- [README.md](./README.md) - 完整项目文档
- [CONTRIBUTION.md](./CONTRIBUTION.md) - 贡献指南
- 各模块都包含详细注释

---

## ✨ 下一步建议

1. 配置数据库连接信息
2. 安装前端依赖并启动前端
3. 配置后端环境变量并启动后端
4. 使用 Postman 测试 API
5. 开发新功能模块
6. 编写单元测试

---

**项目创建时间**: 2026-07-01  
**框架版本**: 1.0.0  
**开发者**: GitHub Copilot
