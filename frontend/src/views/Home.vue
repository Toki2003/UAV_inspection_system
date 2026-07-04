<template>
  <section class="home">

    <!-- 子路由出口（必须有，否则动态路由不会显示） -->
    <router-view />

    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <span>系统总览</span>
          <el-tag :type="apiReady ? 'success' : 'warning'" effect="plain">
            {{ apiReady ? '后端已连接' : '使用本地示例数据' }}
          </el-tag>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6">
          <el-statistic title="总任务数" :value="overview.totalTasks" />
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-statistic title="已完成任务" :value="overview.completedTasks" />
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-statistic title="设备总数" :value="overview.totalDevices" />
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-statistic title="在线设备" :value="overview.onlineDevices" />
        </el-col>
      </el-row>

      <el-divider />

      <p class="info-text">
        该系统采用 Vue 3 + Vite 构建前端，Django + Django REST Framework 构建后端，
        用于无人机巡检任务、设备状态和巡检数据的统一管理。
      </p>

      <el-button type="primary" @click="goToDashboard">
        进入仪表盘
      </el-button>

    </el-card>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getOverview } from '@/api/inspection'

const router = useRouter()

const apiReady = ref(false)

const overview = reactive({
  totalTasks: 4,
  completedTasks: 1,
  activeTasks: 2,
  totalDevices: 3,
  onlineDevices: 2
})

const loadOverview = async () => {
  try {
    const response = await getOverview()
    Object.assign(overview, response.data)
    apiReady.value = true
  } catch (e) {
    apiReady.value = false
  }
}

const goToDashboard = () => {
  router.push('/dashboard')
}

onMounted(loadOverview)
</script>

<style scoped>
.home {
  width: 100%;
}

.welcome-card {
  margin-bottom: 2rem;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  font-size: 1.1rem;
  font-weight: 700;
}

.info-text {
  max-width: 760px;
  color: #606266;
  line-height: 1.7;
}
</style>