<template>
  <div class="home">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <span>欢迎使用 UAV 无人机巡检系统</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6">
          <el-statistic title="总任务数" :value="tasks" />
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-statistic title="完成任务数" :value="completedTasks" />
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-statistic title="设备数" :value="devices" />
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-statistic title="在线设备" :value="onlineDevices" />
        </el-col>
      </el-row>
      <el-divider />
      <p class="info-text">
        这是一个现代化的 UAV 无人机巡检管理系统，提供任务管理、设备监控、数据分析等功能。
      </p>
      <el-button type="primary" @click="goToDashboard">进入仪表板</el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElStatistic, ElButton } from 'element-plus'

const router = useRouter()

const tasks = ref(120)
const completedTasks = ref(85)
const devices = ref(45)
const onlineDevices = ref(38)

const goToDashboard = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.home {
  width: 100%;
}

.welcome-card {
  margin-bottom: 2rem;
}

.card-header {
  font-size: 1.1rem;
  font-weight: bold;
}

.info-text {
  font-size: 1rem;
  color: #606266;
  line-height: 1.6;
}
</style>
