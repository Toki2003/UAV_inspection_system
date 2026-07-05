<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { usePermissionStore } from '@/store/permission'
import { useAppStore } from '@/store'
import {
  Bell,
  ClipboardList,
  Home,
  LogOut,
  Menu,
  Monitor,
  Plane,
  Settings,
  UserRound,
} from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import loginApi from '@/api/login'
import { resetTokenVerification } from '@/router'

const props = defineProps({
  menuVisible: { type: Boolean, required: true },
})

const emit = defineEmits(['toggleMenu'])

const router = useRouter()
const route = useRoute()
const store = useAppStore()
const permissionStore = usePermissionStore()

const platformTitle = '城市轨道交通无人机智能巡检与缺陷管理平台'

const operator = computed(() => ({
  name: store.user?.nickname || '管理员',
  role: store.user?.role?.name || '系统管理员',
}))

const iconMap = {
  '仪表盘': Monitor,
  '系统管理': Settings,
  '告警管理': Bell,
  '无人机管控': Plane,
}

// Static + dynamic menu items
const menuItems = computed(() => {
  const staticItems = [
    { path: '/', title: '首页' },
    { path: '/dashboard', title: '仪表盘' },
  ]
  const dynamicItems = permissionStore.menus.filter(
    (m) => m.path !== '/dashboard'
  )
  return [...staticItems, ...dynamicItems]
})

function iconFor(title) {
  return iconMap[title] || Home
}

function isActive(item) {
  return route.path === item.path
}

function navigate(item) {
  if (item.path !== route.path) {
    router.push(item.path)
  }
}

async function handleLogout() {
  await loginApi.logout()
  store.clearAuth()
  permissionStore.reset()
  resetTokenVerification()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<template>
  <header class="topbar">
    <div class="brand">
      <span class="brand-mark" aria-hidden="true"><Plane :size="18" /></span>
      <h1>{{ platformTitle }}</h1>
    </div>

    <nav v-show="menuVisible" class="main-menu" aria-label="顶部菜单栏">
      <button
        v-for="item in menuItems"
        :key="item.path"
        class="menu-item"
        :class="{ active: isActive(item) }"
        type="button"
        @click="navigate(item)"
      >
        <component :is="iconFor(item.title)" :size="16" />
        <span>{{ item.title }}</span>
      </button>
    </nav>

    <div class="top-actions">
      <button
        class="icon-button menu-toggle"
        type="button"
        :title="menuVisible ? '隐藏顶部菜单栏' : '显示顶部菜单栏'"
        @click="emit('toggleMenu')"
      >
        <Menu :size="20" />
      </button>
      <button class="user-button" type="button">
        <UserRound :size="17" />
        <span>
          {{ operator.name }}
          <small>{{ operator.role }}</small>
        </span>
      </button>
      <button
        class="icon-button exit-button"
        type="button"
        title="退出系统"
        @click="handleLogout"
      >
        <LogOut :size="18" />
      </button>
    </div>
  </header>
</template>
