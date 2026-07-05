import { createRouter, createWebHistory } from 'vue-router'
import { useAppStore } from '@/store'
import { usePermissionStore } from '@/store/permission'

const Layout = () => import('@/layout/index.vue')

const constantRoutes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    name: 'Layout',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/about',
        name: 'About',
        component: () => import('@/views/About.vue'),
        meta: { requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes: constantRoutes
})

// 标记是否已验证过 token（避免每次路由都请求后端）
let tokenVerified = false

router.beforeEach((to, from, next) => {
  const store = useAppStore()
  const token = store.token || localStorage.getItem('token')

  if (!to.meta.public && !token) {
    return next('/login')
  }

  if (token && !tokenVerified) {
    return verifyToken(store).then(valid => {
      if (!valid) {
        store.clearAuth()
        tokenVerified = false
        return next('/login')
      }

      tokenVerified = true

      const permissionStore = usePermissionStore()
      if (!permissionStore.routesAdded) {
        const role = store.user?.role?.name || 'user'
        const permissions = store.permissions || []
        permissionStore.generateRoutes(role, permissions)
        return next({ ...to, replace: true })
      }

      next()
    }).catch(() => {
      store.clearAuth()
      tokenVerified = false
      return next('/login')
    })
  }

  const permissionStore = usePermissionStore()
  if (token && !permissionStore.routesAdded) {
    const role = store.user?.role?.name || 'user'
    const permissions = store.permissions || []
    permissionStore.generateRoutes(role, permissions)
    return next({ ...to, replace: true })
  }

  next()
})

/**
 * 向后端验证 token 是否有效
 * 调用 /api/system/userinfo 接口，检查响应 body 中的 code 是否为 200
 */
function verifyToken(store) {
  return fetch('/api/system/userinfo', {
    headers: { 'Authorization': `Bearer ${store.token}` }
  }).then(res => {
    if (!res.ok) return false
    return res.json().then(data => {
      // 后端返回 { code: 200, data: {...} } 才视为有效
      if (data.code === 200 && data.data) {
        store.setUser(data.data)
        return true
      }
      return false
    })
  }).catch(() => false)
}

// 登出时重置验证状态
export function resetTokenVerification() {
  tokenVerified = false
}

export default router