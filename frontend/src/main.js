import { createApp } from 'vue'
import App from './App.vue'

import router from './router'
import { createPinia } from 'pinia'

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './style.css'

import { useAppStore } from './store'
import { usePermissionStore } from './store/permission'
import permission from './directives/permission'

// 创建应用
const app = createApp(App)

const pinia = createPinia()
app.use(pinia)

// 恢复登录状态
const store = useAppStore()
store.initAuth()

// 若有已保存的 token，在挂载 router 前预加载动态路由
if (store.token) {
  const role = store.user?.role?.name || 'user'
  const permissions = store.permissions || []
  usePermissionStore().generateRoutes(role, permissions)
}

// 挂载 router
app.use(router)

app.use(ElementPlus)

// 指令
app.directive('permission', permission)

// 挂载
app.mount('#app')
