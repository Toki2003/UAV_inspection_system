<template>
  <div class="app-container">
    <header class="app-header" v-if="isAuthenticated">
      <div class="header-inner">
        <h1>UAV 无人机巡检系统</h1>
        <nav class="nav">
          <router-link to="/">首页</router-link>
          <router-link to="/dashboard">仪表盘</router-link>
          <!-- 动态菜单：从 permissionStore 获取，避免路由未注册时的警告 -->
          <router-link
            v-for="item in permissionStore.menus"
            :key="item.path"
            :to="item.path"
          >{{ item.title }}</router-link>
          <router-link to="/about">关于</router-link>
          <span class="nav-divider">|</span>
          <span class="user-info">
            {{ store.user?.nickname || JSON.parse(localStorage.getItem('user') || '{}')?.nickname || '用户' }}
          </span>
          <el-button type="danger" size="small" plain @click="handleLogout">退出登录</el-button>
        </nav>
      </div>
    </header>

    <main class="app-main">
      <router-view />
    </main>

    <footer class="app-footer" v-if="isAuthenticated">
      <p>&copy; 2026 UAV 巡检系统</p>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import loginApi from './api/login'
import { useAppStore } from './store'
import { usePermissionStore } from './store/permission'
import { resetTokenVerification } from './router'

const router = useRouter()
const store = useAppStore()
const permissionStore = usePermissionStore()

const isAuthenticated = computed(() => {
  return !!(store.token || localStorage.getItem('token'))
})

const handleLogout = async () => {
  await loginApi.logout()

  // 1. 清除 app store（token/user/permissions）
  store.clearAuth()

  // 2. 重置 permissionStore（routesAdded/menus）
  permissionStore.reset()

  // 3. 重置 token 验证状态（下次进入需重新验证）
  resetTokenVerification()

  // 4. 跳转登录页
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background: #243447;
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
}

.app-header h1 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
}

.nav {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
}

.nav a {
  color: rgba(255, 255, 255, 0.82);
  text-decoration: none;
  transition: color 0.2s;
}

.nav a.router-link-active,
.nav a:hover {
  color: #8bd3dd;
}

.nav-divider {
  color: rgba(255, 255, 255, 0.3);
}

.user-info {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.875rem;
}

.app-main {
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.app-footer {
  background-color: #f5f7fa;
  color: #606266;
  text-align: center;
  padding: 1rem;
  border-top: 1px solid #ebeef5;
}

.app-footer p {
  margin: 0;
}

@media (max-width: 768px) {
  .header-inner {
    align-items: flex-start;
    flex-direction: column;
    padding: 1rem;
  }

  .app-main {
    padding: 1rem;
  }
}
</style>
