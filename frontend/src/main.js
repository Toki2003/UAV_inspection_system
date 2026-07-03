import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { useAppStore } from './store'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 启动时从 localStorage 恢复登录状态
const store = useAppStore()
store.initAuth()

app.mount('#app')
