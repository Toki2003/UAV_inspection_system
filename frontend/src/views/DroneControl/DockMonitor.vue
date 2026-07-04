<template>
  <section class="dock-monitor">
    <!-- 统计信息 -->
    <el-row
      :gutter="16"
      class="overview-row"
    >
      <el-col
        :xs="12"
        :sm="12"
        :md="6"
      >
        <el-card shadow="hover">
          <el-statistic
            title="机库总数"
            :value="overview.totalCount"
          />
        </el-card>
      </el-col>

      <el-col
        :xs="12"
        :sm="12"
        :md="6"
      >
        <el-card shadow="hover">
          <el-statistic
            title="在线机库"
            :value="overview.onlineCount"
          />
        </el-card>
      </el-col>

      <el-col
        :xs="12"
        :sm="12"
        :md="6"
      >
        <el-card shadow="hover">
          <el-statistic
            title="离线机库"
            :value="overview.offlineCount"
          />
        </el-card>
      </el-col>

      <el-col
        :xs="12"
        :sm="12"
        :md="6"
      >
        <el-card shadow="hover">
          <el-statistic
            title="告警机库"
            :value="overview.alarmCount"
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- 机库卡片 -->
    <el-card class="dock-panel">
      <template #header>
        <div class="panel-header">
          <span>机场/机库状态监控</span>

          <el-button
            type="primary"
            link
            :loading="loading"
            @click="loadDockData"
          >
            刷新
          </el-button>
        </div>
      </template>

      <el-row :gutter="16">
        <el-col
          v-for="dock in docks"
          :key="dock.dockCode"
          :xs="24"
          :sm="12"
          :lg="8"
        >
          <el-card
            shadow="hover"
            class="dock-card"
            :class="{
              'dock-card-alarm': dock.alarm,
              'dock-card-offline':
                dock.status === 'offline'
            }"
          >
            <div class="dock-title">
              <div>
                <h3>{{ dock.dockName }}</h3>
                <span>{{ dock.dockCode }}</span>
              </div>

              <div class="dock-tags">
                <el-tag
                  :type="
                    dock.status === 'online'
                      ? 'success'
                      : 'danger'
                  "
                >
                  {{
                    dock.status === 'online'
                      ? '在线'
                      : '离线'
                  }}
                </el-tag>

                <el-tag
                  v-if="dock.alarm"
                  type="danger"
                >
                  告警
                </el-tag>
              </div>
            </div>

            <el-descriptions
              :column="2"
              size="small"
              border
            >
              <el-descriptions-item
                label="位置"
                :span="2"
              >
                {{ dock.location }}
              </el-descriptions-item>

              <el-descriptions-item label="温度">
                {{ dock.temperature }}℃
              </el-descriptions-item>

              <el-descriptions-item label="湿度">
                {{ dock.humidity }}%
              </el-descriptions-item>

              <el-descriptions-item label="风速">
                {{ dock.windSpeed }} m/s
              </el-descriptions-item>

              <el-descriptions-item label="舱盖">
                {{ coverStatusText(dock.coverStatus) }}
              </el-descriptions-item>

              <el-descriptions-item label="无人机在库">
                {{ dock.droneInDock ? '是' : '否' }}
              </el-descriptions-item>

              <el-descriptions-item label="无人机">
                {{ dock.droneCode || '--' }}
              </el-descriptions-item>

              <el-descriptions-item label="电量">
                {{ dock.battery }}%
              </el-descriptions-item>

              <el-descriptions-item label="存储占用">
                {{ dock.storageUsage }}%
              </el-descriptions-item>

              <el-descriptions-item label="关联任务">
                {{ dock.taskCount }}
              </el-descriptions-item>

              <el-descriptions-item
                label="更新时间"
                :span="2"
              >
                {{ formatTime(dock.updateTime) }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>

      <el-empty
        v-if="!loading && docks.length === 0"
        description="暂无机库数据"
      />
    </el-card>
  </section>
</template>

<script setup>
import {
  onMounted,
  onUnmounted,
  reactive,
  ref
} from 'vue'
import { ElMessage } from 'element-plus'

import {
  getDockList,
  getDockOverview
} from '@/api/droneControl'


const loading = ref(false)
const docks = ref([])

const overview = reactive({
  totalCount: 0,
  onlineCount: 0,
  offlineCount: 0,
  alarmCount: 0
})

let dockTimer = null


async function loadDockData() {
  loading.value = true

  try {
    const [
      overviewResponse,
      listResponse
    ] = await Promise.all([
      getDockOverview(),
      getDockList()
    ])

    if (overviewResponse.code === 200) {
      Object.assign(
        overview,
        overviewResponse.data
      )
    } else {
      ElMessage.error(
        overviewResponse.message
      )
    }

    if (listResponse.code === 200) {
      docks.value = listResponse.data || []
    } else {
      ElMessage.error(
        listResponse.message
      )
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取机库状态失败')
  } finally {
    loading.value = false
  }
}


function coverStatusText(status) {
  const statusMap = {
    open: '已打开',
    closed: '已关闭',
    unknown: '未知'
  }

  return statusMap[status] || '未知'
}


function formatTime(timestamp) {
  if (!timestamp) {
    return '--'
  }

  return new Date(timestamp).toLocaleString()
}


onMounted(() => {
  loadDockData()

  dockTimer = window.setInterval(
    loadDockData,
    10000
  )
})


onUnmounted(() => {
  if (dockTimer) {
    window.clearInterval(dockTimer)
    dockTimer = null
  }
})
</script>

<style scoped>
.overview-row {
  margin-bottom: 20px;
}

.overview-row .el-col {
  margin-bottom: 16px;
}

.dock-panel {
  margin-bottom: 20px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.dock-card {
  margin-bottom: 16px;
}

.dock-card-alarm {
  border-color: #f56c6c;
}

.dock-card-offline {
  opacity: 0.75;
}

.dock-title {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.dock-title h3 {
  margin: 0 0 4px;
  color: #303133;
}

.dock-title span {
  color: #909399;
  font-size: 13px;
}

.dock-tags {
  display: flex;
  gap: 6px;
}
</style>