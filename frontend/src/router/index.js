import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue')
  },
  // ========== 新增告警管理路由 ==========
  {
    path: '/alert',
    name: 'AlertManage',
    component: () => import('@/views/AlertManage/index.vue'),
    meta: { title: '告警管理' }
  }
  // ======================================
]

const router = createRouter({
  history: createWebHistory(),
  routes  // 注意：这里必须加上 routes 字段！
})

export default router