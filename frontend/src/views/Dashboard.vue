<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <el-statistic title="活跃任务" :value="activeTasks" />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <el-statistic title="飞行小时" :value="flightHours" />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <el-statistic title="检测区域" :value="areas" />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <el-statistic title="系统状态" value="正常" />
        </el-card>
      </el-col>
    </el-row>

    <el-card class="dashboard-card" style="margin-top: 2rem">
      <template #header>
        <div class="card-header">
          <span>仪表板</span>
        </div>
      </template>
      <el-table :data="taskData" style="width: 100%">
        <el-table-column prop="id" label="任务ID" width="100" />
        <el-table-column prop="name" label="任务名称" width="200" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '已完成' ? 'success' : 'info'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="150" />
        <el-table-column label="操作" width="150">
          <template #default>
            <el-button link type="primary">详情</el-button>
            <el-button link type="danger">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElStatistic, ElCard, ElTable, ElTableColumn, ElTag, ElButton } from 'element-plus'

const activeTasks = ref(12)
const flightHours = ref(856)
const areas = ref(23)

const taskData = ref([
  { id: 1, name: '电力线巡检', status: '进行中', progress: '65%' },
  { id: 2, name: '建筑检测', status: '已完成', progress: '100%' },
  { id: 3, name: '农业监测', status: '进行中', progress: '45%' },
  { id: 4, name: '环境评估', status: '未开始', progress: '0%' }
])
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.stat-card {
  height: 100%;
}

.dashboard-card {
  margin-top: 2rem;
}

.card-header {
  font-size: 1.1rem;
  font-weight: bold;
}
</style>
