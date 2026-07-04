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

        <!-- 用户管理 -->
        <el-tab-pane label="账户管理" name="user">
          <UserTable />
        </el-tab-pane>

        <!-- 角色管理 -->
        <el-tab-pane label="角色管理" name="role">
          <RoleTable />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

import DockMonitor from '@/views/DroneControl/DockMonitor.vue'
import UserTable from './components/UserTable.vue'
import RoleTable from './components/RoleTable.vue'

const activeTab = ref('airport')
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
