<template>
  <div class="system-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统权限管理</span>
          <span class="desc">管理人员账号和角色</span>
        </div>
      </template>

      <el-tabs v-model="activeTab" type="border-card">
        <el-tab-pane label="机场监控" name="airport">
          <DockMonitor />
        </el-tab-pane>

        <!-- 用户管理：需要 user:view 权限 -->
        <el-tab-pane v-if="hasUserView" label="账户管理" name="user">
          <UserTable />
        </el-tab-pane>

        <!-- 角色管理：需要 role:view 权限 -->
        <el-tab-pane v-if="hasRoleView" label="角色管理" name="role">
          <RoleTable />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
/**
 * SystemManage - 系统权限管理页面
 *
 * 包含多个 Tab 页：机场监控、账户管理、角色管理。
 * 各 Tab 根据用户权限动态显示 / 隐藏，权限不足时自动切换到默认可见 Tab。
 */
import { ref, computed, watch } from 'vue'
import { useAppStore } from '@/store'
import { expandPermissions } from '@/utils/permission'

import DockMonitor from '@/views/DroneControl/DockMonitor.vue'
import UserTable from './components/UserTable.vue'
import RoleTable from './components/RoleTable.vue'

const store = useAppStore()

/** 是否有用户管理查看权限（user:view） */
const hasUserView = computed(() => {
  const perms = expandPermissions(store.permissions || [])
  return perms.includes('user:view')
})

/** 是否有角色管理查看权限（role:view） */
const hasRoleView = computed(() => {
  const perms = expandPermissions(store.permissions || [])
  return perms.includes('role:view')
})

const activeTab = ref('airport')

/** 权限变化时，如果当前 tab 被隐藏，自动切换到默认可见 Tab */
watch([hasUserView, hasRoleView], () => {
  if (activeTab.value === 'user' && !hasUserView.value) {
    activeTab.value = 'airport'
  }
  if (activeTab.value === 'role' && !hasRoleView.value) {
    activeTab.value = 'airport'
  }
}, { immediate: true })
</script>

<style scoped>
.system-manage {
  width: 100%;
}

.card-header {
  display: flex;
  align-items: baseline;
  gap: 1rem;
}

.desc {
  font-size: 0.85rem;
  color: #909399;
}
</style>
