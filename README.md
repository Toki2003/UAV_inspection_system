# UAV 无人机巡检系统

## 项目概述

这是一个现代化的无人机巡检管理系统，集成了先进的飞行控制、数据处理和可视化分析技术。系统包含前端和后端两个部分：

- **前端**: Vue 3 + Vite + Element Plus
- **后端**: Spring Boot + JDK 1.8 + MySQL + Redis

## 项目结构

```
UAV_inspection_system/
├── frontend/              # 前端项目（Vue 3）
│   ├── src/
│   │   ├── components/    # 组件目录
│   │   ├── views/         # 页面目录
│   │   ├── api/           # API 请求模块
│   │   ├── router/        # 路由配置
│   │   ├── store/         # 状态管理（Pinia）
│   │   ├── App.vue        # 根组件
│   │   └── main.js        # 入口文件
│   ├── public/            # 静态资源
│   ├── index.html         # 入口 HTML
│   ├── package.json       # 项目依赖
│   ├── vite.config.js     # Vite 配置
│   └── .gitignore
│
└── backend/               # 后端项目（Spring Boot）
    ├── src/
    │   ├── main/
    │   │   ├── java/com/uav/inspection/
    │   │   │   ├── controller/      # 控制层
    │   │   │   ├── service/         # 业务逻辑层
    │   │   │   ├── dao/             # 数据访问层
    │   │   │   ├── entity/          # 实体类
    │   │   │   ├── util/            # 工具类
    │   │   │   └── UavInspectionApplication.java  # 启动类
    │   │   └── resources/
    │   │       └── application.yml  # 配置文件
    │   └── test/
    ├── pom.xml            # Maven 配置
    └── .gitignore
```

## 快速开始

### 前端开发

1. 进入前端目录:
```bash
cd frontend
```

2. 安装依赖:
```bash
npm install
```

3. 启动开发服务器:
```bash
npm run dev
```

开发服务器将在 `http://localhost:5173` 运行

4. 构建生产版本:
```bash
npm run build
```

### 后端开发

#### 环境要求
- JDK 1.8+
- Maven 3.6+
- MySQL 5.7+
- Redis 5.0+

1. 进入后端目录:
```bash
cd backend
```

2. 配置数据库:
   - 修改 `src/main/resources/application.yml` 中的数据库连接信息
   - 创建数据库: `uav_inspection`

3. 编译项目:
```bash
mvn clean compile
```

4. 运行项目:
```bash
mvn spring-boot:run
```

或者先打包:
```bash
mvn clean package
java -jar target/inspection-system-1.0.0.jar
```

后端服务将在 `http://localhost:8080` 运行

## 功能模块

### 前端功能
- 首页仪表板
- 任务管理（创建、编辑、删除、查询）
- 设备管理（在线状态、电池监控）
- 数据展示和统计

### 后端功能
- RESTful API 接口
- 任务管理服务
- 设备管理服务
- 数据库持久化（JPA/Hibernate）
- 缓存管理（Redis）
- 统一的API响应格式

## API 文档

### 巡检任务相关

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/inspection/list` | 获取任务列表 |
| GET | `/api/inspection/{id}` | 获取任务详情 |
| POST | `/api/inspection/create` | 创建任务 |
| PUT | `/api/inspection/{id}` | 更新任务 |
| DELETE | `/api/inspection/{id}` | 删除任务 |
| GET | `/api/inspection/device/{deviceId}` | 获取设备的任务 |
| GET | `/api/inspection/status/{status}` | 根据状态获取任务 |

### 设备相关

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/device/list` | 获取设备列表 |
| GET | `/api/device/{id}` | 获取设备详情 |
| GET | `/api/device/code/{code}` | 根据代码获取设备 |
| POST | `/api/device/create` | 创建设备 |
| PUT | `/api/device/{id}` | 更新设备 |
| DELETE | `/api/device/{id}` | 删除设备 |
| GET | `/api/device/online` | 获取在线设备 |
| GET | `/api/device/online/count` | 获取在线设备数量 |

## 技术栈详情

### 前端
- **Vue 3**: 渐进式 JavaScript 框架
- **Vite**: 下一代前端构建工具
- **Pinia**: Vue 3 官方状态管理库
- **Axios**: HTTP 客户端
- **Element Plus**: Vue 3 UI 组件库

### 后端
- **Spring Boot 2.7.17**: 快速开发框架
- **Spring Data JPA**: ORM 框架
- **MySQL**: 数据库
- **Redis**: 缓存存储
- **Lombok**: 代码简化工具
- **FastJSON**: JSON 处理库

## 配置说明

### 前端配置 (vite.config.js)
- 开发服务器端口: 5173
- API 代理: `/api` 代理到 `http://localhost:8080`

### 后端配置 (application.yml)
- 服务器端口: 8080
- 数据库: MySQL (localhost:3306/uav_inspection)
- Redis: localhost:6379
- JPA 自动建表: update

## 开发规范

### 前端
- 使用 Vue 3 Composition API
- 组件使用 `<script setup>` 语法
- CSS 使用 scoped 样式
- API 请求统一通过 `src/api` 模块

### 后端
- 使用 RESTful 风格设计 API
- 统一使用 `ApiResponse` 包装响应
- 按照分层架构组织代码（controller -> service -> dao）
- 使用 Lombok 简化实体类

## 常见问题

1. **前端何时连接到后端?**
   - 前端通过 `/api` 代理自动转发到 `http://localhost:8080`
   - 确保后端服务正在运行

2. **如何修改数据库连接?**
   - 修改 `backend/src/main/resources/application.yml` 中的数据源配置

3. **如何添加新的 API 端点?**
   - 在 `controller` 中创建对应的控制器类
   - 在 `service` 中实现业务逻辑
   - 在 `dao` 仓库中定义数据访问方法

## 许可证

MIT License

## 版本信息

- 前端版本: 1.0.0
- 后端版本: 1.0.0
