# Contribution

感谢参与 UAV 无人机巡检系统开发。

## 开发流程

1. 创建功能分支：`git checkout -b feature/your-feature`
2. 完成开发和本地验证
3. 提交变更：`git commit -m "feat: add your feature"`
4. 推送分支并创建 Pull Request

## 代码规范

### 前端

- 使用 Vue 3 Composition API。
- 页面组件优先使用 `<script setup>`。
- API 请求统一放在 `frontend/src/api`。
- 路由配置统一放在 `frontend/src/router/index.js`。
- 组件和页面命名使用 PascalCase，变量命名使用 camelCase。

### 后端

- 使用 Django + Django REST Framework。
- 业务模块放在 `backend/apps`。
- 模型定义放在 `models.py`，序列化放在 `serializers.py`，接口视图放在 `views.py`。
- 新增模型后执行 `python manage.py makemigrations` 和 `python manage.py migrate`。
- API 返回统一使用 `apps.inspection.responses` 中的 `success` 和 `fail`。

## 提交信息

推荐格式：

```text
<type>(<scope>): <subject>
```

常用类型：

- `feat`：新功能
- `fix`：缺陷修复
- `docs`：文档
- `style`：格式调整
- `refactor`：重构
- `test`：测试
- `chore`：工程配置

## 本地验证

后端：

```bash
cd backend
python manage.py check
python manage.py test
```

前端：

```bash
cd frontend
npm run build
```
