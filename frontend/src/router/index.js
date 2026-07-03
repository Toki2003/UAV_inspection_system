import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { public: true }       // 不需要登录就能访问
  },
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }  // 需要登录
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
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
    // 公共页面（登录页）：已登录则跳首页
    token ? next('/') : next()
  } else {
    // 需要登录的页面：没 token 跳登录页
    token ? next() : next('/login')
  }
})

export default router
