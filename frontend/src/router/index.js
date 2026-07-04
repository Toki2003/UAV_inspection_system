import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { public: true }
  },
  {
  path: '/drone-control',
  name: 'DroneControl',
  component: () =>
    import('@/views/DroneControl/index.vue'),
  meta: {
    title: '无人机管控',
    requiresAuth: true
  }
},
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/alert',
    name: 'AlertManage',
    component: () => import('@/views/AlertManage/index.vue'),
    meta: { title: '告警管理', requiresAuth: true }
  },
  {
    path: '/inspection-tasks',
    name: 'InspectionTasks',
    component: () => import('@/views/InspectionTasks.vue'),
    meta: { title: '巡检任务', requiresAuth: true }
  },
  {
    path: '/inspection-tasks/:id',
    name: 'InspectionTaskDetail',
    component: () => import('@/views/InspectionTaskDetail.vue'),
    meta: { title: '巡检任务详情', requiresAuth: true }
  },
  {
    path: '/system',
    name: 'SystemManage',
    component: () => import('@/views/SystemManage/index.vue'),
    meta: { title: '系统管理', requiresAuth: true }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 —— 没登录就跳到登录页
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.meta.public) {
    token ? next('/') : next()
  } else {
    token ? next() : next('/login')
  }
})

export default router
