<template>
  <section class="dashboard">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <el-statistic title="活跃任务" :value="overview.activeTasks" />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <el-statistic title="总任务数" :value="overview.totalTasks" />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <el-statistic title="在线设备" :value="overview.onlineDevices" />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <el-statistic title="系统状态" value="正常" />
        </el-card>
      </el-col>
    </el-row>

    <el-card class="dashboard-card">
      <template #header>
        <div class="card-header">
          <span>巡检任务</span>
          <el-button type="primary" plain @click="loadData">刷新</el-button>
        </div>
      </template>

      <el-table :data="taskData" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="任务ID" width="100" />
        <el-table-column prop="name" label="任务名称" min-width="180" />
        <el-table-column prop="device_name" label="执行设备" min-width="140" />
        <el-table-column prop="area" label="巡检区域" min-width="140" />
        <el-table-column prop="status_display" label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">
              {{ row.status_display || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="180">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :stroke-width="10" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { getInspectionList, getOverview } from '@/api/inspection'

const loading = ref(false)

const overview = reactive({
  totalTasks: 4,
  activeTasks: 2,
  onlineDevices: 2
})

const taskData = ref([
  { id: 1, name: '电力线路巡检', device_name: '巡检一号', area: 'A 区', status: 'running', status_display: '执行中', progress: 65 },
  { id: 2, name: '建筑外立面检测', device_name: '巡检二号', area: 'B 区', status: 'completed', status_display: '已完成', progress: 100 },
  { id: 3, name: '农田监测', device_name: '巡检三号', area: 'C 区', status: 'pending', status_display: '待执行', progress: 0 }
])

const statusTagType = (status) => {
  const map = {
    completed: 'success',
    running: 'primary',
    pending: 'info',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const [overviewResponse, taskResponse] = await Promise.all([
      getOverview(),
      getInspectionList()
    ])
    Object.assign(overview, overviewResponse.data)
    taskData.value = taskResponse.data
  } catch {
    // Keep local demo data when the backend is not running.
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.stat-card {
  height: 100%;
  margin-bottom: 1rem;
}

.dashboard-card {
  margin-top: 1rem;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  font-size: 1.1rem;
  font-weight: 700;
}
</style>
