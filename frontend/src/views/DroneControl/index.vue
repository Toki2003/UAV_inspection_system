<template>
  <section class="drone-control">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2>无人机管控</h2>
        <p>查看无人机实时状态并发送控制命令</p>
      </div>

      <div class="header-actions">
        <el-select
          v-model="selectedDeviceCode"
          placeholder="请选择无人机"
          @change="handleDeviceChange"
        >
          <el-option
            v-for="device in devices"
            :key="device.code"
            :label="`${device.name}（${device.code}）`"
            :value="device.code"
          />
        </el-select>

        <el-button
          type="primary"
          :loading="telemetryLoading"
          @click="loadTelemetry"
        >
        刷新状态
        </el-button>
      </div>
    </div>

<!-- 机场监控 -->
    <DockMonitor />

    <!-- 实时状态 -->
    <el-card class="panel">
      <template #header>
        <div class="panel-header">
          <span>无人机实时状态</span>

          <el-tag
            v-if="telemetry"
            :type="telemetry.online ? 'success' : 'danger'"
          >
            {{ telemetry.online ? '在线' : '离线' }}
          </el-tag>
        </div>
      </template>

      <el-descriptions
        v-if="telemetry"
        :column="3"
        border
      >
      <el-descriptions-item label="设备编号">
          {{ telemetry.deviceCode }}
        </el-descriptions-item>

        <el-descriptions-item label="设备名称">
          {{ telemetry.deviceName }}
        </el-descriptions-item>

        <el-descriptions-item label="设备型号">
          {{ telemetry.deviceModel || '--' }}
        </el-descriptions-item>

        <el-descriptions-item label="剩余电量">
          <el-progress
            :percentage="telemetry.battery"
            :stroke-width="12"
          />
        </el-descriptions-item>

        <el-descriptions-item label="飞行高度">
          {{ telemetry.height }} 米
        </el-descriptions-item>

        <el-descriptions-item label="飞行速度">
          {{ telemetry.speed }} 米/秒
        </el-descriptions-item>

        <el-descriptions-item label="经度">
          {{ telemetry.longitude }}
        </el-descriptions-item>

        <el-descriptions-item label="纬度">
          {{ telemetry.latitude }}
        </el-descriptions-item>

        <el-descriptions-item label="当前位置">
          {{ telemetry.location || '--' }}
        </el-descriptions-item>

        <el-descriptions-item label="飞行状态">
          <el-tag type="primary">
            {{ telemetry.flightStatus }}
          </el-tag>
        </el-descriptions-item>

        <el-descriptions-item label="告警状态">
          <el-tag
            :type="
              telemetry.alarmStatus === '正常'
                ? 'success'
                : 'danger'
            "
          >
            {{ telemetry.alarmStatus }}
          </el-tag>
        </el-descriptions-item>

<el-descriptions-item label="飞行合规">
  <el-tag
    :type="
      telemetry.complianceStatus === '合规'
        ? 'success'
        : 'danger'
    "
  >
    {{ telemetry.complianceStatus }}
  </el-tag>
</el-descriptions-item>

<el-descriptions-item label="禁飞区状态">
  <el-tag
    :type="
      telemetry.inNoFlyZone
        ? 'danger'
        : 'success'
    "
  >
    {{
      telemetry.inNoFlyZone
        ? '位于禁飞区'
        : '未进入禁飞区'
    }}
  </el-tag>
</el-descriptions-item>

<el-descriptions-item label="传输安全">
  <el-tag
    :type="
      telemetry.encrypted
        ? 'success'
        : 'warning'
    "
  >
    {{
      telemetry.encrypted
        ? '已加密'
        : '未加密'
    }}
  </el-tag>
</el-descriptions-item>

        <el-descriptions-item label="更新时间">
          {{ formatTime(telemetry.updateTime) }}
        </el-descriptions-item>
      </el-descriptions>

      <el-empty
        v-else
        description="暂未获取无人机状态"
      />
    </el-card>

    <!-- 视频区域 -->
    <el-card class="panel">
      <template #header>
        <div class="panel-header">
          <span>实时视频</span>

          <el-tag
            v-if="videoInfo"
            :type="
              videoInfo.videoAvailable
                ? 'success'
                : 'danger'
            "
          >
            {{
              videoInfo.videoAvailable
                ? '视频流可用'
                : '视频流不可用'
            }}
          </el-tag>
        </div>
      </template>

      <div class="video-container">
        <div class="video-placeholder">
          <span class="video-title">
            实时视频预留区域
          </span>

          <span v-if="videoInfo">
            视频协议：
            {{ videoInfo.videoProtocol }}
          </span>

          <span v-if="videoInfo">
            视频地址：
            {{ videoInfo.videoUrl }}
          </span>

          <span class="video-note">
            当前仅预留视频流地址，后期接入FLV播放器
          </span>
        </div>
      </div>
    </el-card>

    <!-- 飞行控制 -->
    <el-card class="panel">
      <template #header>
        <span>飞行控制</span>
      </template>

      <div class="command-buttons">
        <el-button
          type="danger"
          :loading="commandLoading"
          :disabled="!canControl"
          @click="handleCommand('RETURN_HOME')"
        >
          返航
        </el-button>

        <el-button
          :loading="commandLoading"
          :disabled="!canControl"
          @click="
            handleCommand('CANCEL_RETURN_HOME')
          "
        >
          取消返航
        </el-button>

        <el-button
          type="warning"
          :loading="commandLoading"
          :disabled="!canControl"
          @click="handleCommand('PAUSE')"
        >
          暂停
        </el-button>

        <el-button
          type="success"
          :loading="commandLoading"
          :disabled="!canControl"
          @click="handleCommand('RESUME')"
        >
          恢复
        </el-button>

        <el-button
          type="primary"
          :loading="commandLoading"
          :disabled="!canControl"
          @click="
            handleCommand('START_INSPECTION')
          "
        >
          开始检测
        </el-button>
      </div>

      <el-alert
        v-if="telemetry && !telemetry.online"
        title="当前无人机离线，无法发送控制命令"
        type="warning"
        :closable="false"
        show-icon
        class="offline-alert"
      />
    </el-card>
  </section>
</template>

<script setup>
import {
  computed,
  onMounted,
  onUnmounted,
  ref
} from 'vue'
import {
  ElMessage,
  ElMessageBox
} from 'element-plus'
import DockMonitor from './DockMonitor.vue'

import { getDeviceList } from '@/api/inspection'
import {
  getDroneTelemetry,
  getDroneVideo,
  sendDroneCommand
} from '@/api/droneControl'


const devices = ref([])


const selectedDeviceCode = ref('')

const telemetry = ref(null)

const videoInfo = ref(null)

const telemetryLoading = ref(false)
const commandLoading = ref(false)

let telemetryTimer = null

const canControl = computed(() => {
  return Boolean(
    selectedDeviceCode.value &&
    telemetry.value &&
    telemetry.value.online
  )
})

async function loadDevices() {
  try {
    const response = await getDeviceList()

    if (response.code !== 200) {
      ElMessage.error(response.message)
      return
    }

    devices.value = response.data || []

    if (devices.value.length === 0) {
      ElMessage.warning('当前没有可用设备')
      return
    }

    // 优先选择在线设备
    const onlineDevice = devices.value.find(
      device => device.status === 'online'
    )

    selectedDeviceCode.value = onlineDevice
      ? onlineDevice.code
      : devices.value[0].code

    await loadDroneData()
  } catch (error) {
    console.error(error)
    ElMessage.error('获取设备列表失败')
  }
}

async function loadTelemetry() {
  if (!selectedDeviceCode.value) {
    return
  }

  telemetryLoading.value = true

  try {
    const response = await getDroneTelemetry(
      selectedDeviceCode.value
    )

    if (response.code === 200) {
      telemetry.value = response.data
    } else {
      ElMessage.error(response.message)
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取无人机状态失败')
  } finally {
    telemetryLoading.value = false
  }
}

async function loadVideo() {
  if (!selectedDeviceCode.value) {
    return
  }

  try {
    const response = await getDroneVideo(
      selectedDeviceCode.value
    )

    if (response.code === 200) {
      videoInfo.value = response.data
    } else {
      ElMessage.error(response.message)
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取视频地址失败')
  }
}

async function loadDroneData() {
  await Promise.all([
    loadTelemetry(),
    loadVideo()
  ])
}

async function handleDeviceChange() {
  telemetry.value = null
  videoInfo.value = null

  await loadDroneData()
}

async function handleCommand(command) {
  if (!selectedDeviceCode.value) {
    ElMessage.warning('请先选择无人机')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确认向设备 ${selectedDeviceCode.value} 发送该控制命令吗？`,
      '控制确认',
      {
        confirmButtonText: '确认发送',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    return
  }

  commandLoading.value = true

  try {
    const response = await sendDroneCommand(
      selectedDeviceCode.value,
      command
    )

    if (response.code === 200) {
      ElMessage.success(response.data.message)

      // 命令执行后重新查询状态
      await loadTelemetry()
    } else {
      ElMessage.error(response.message)
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('控制命令发送失败')
  } finally {
    commandLoading.value = false
  }
}

function formatTime(timestamp) {
  if (!timestamp) {
    return '--'
  }

  return new Date(timestamp).toLocaleString()
}

function startTelemetryTimer() {
  stopTelemetryTimer()

  telemetryTimer = window.setInterval(() => {
    loadTelemetry()
  }, 5000)
}

function stopTelemetryTimer() {
  if (telemetryTimer) {
    window.clearInterval(telemetryTimer)
    telemetryTimer = null
  }
}

onMounted(async () => {
  await loadDevices()
  startTelemetryTimer()
})

onUnmounted(() => {
  stopTelemetryTimer()
})
</script>

<style scoped>
.drone-control {
  width: 100%;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px;
}

.page-header p {
  margin: 0;
  color: #909399;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-actions .el-select {
  width: 240px;
}

.panel {
  margin-bottom: 20px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.video-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  min-height: 360px;
  padding: 20px;
  color: #c0c4cc;
  background: #1d1e1f;
  border-radius: 6px;
}

.video-title {
  color: #ffffff;
  font-size: 20px;
  font-weight: 600;
}

.video-note {
  color: #909399;
  font-size: 13px;
}

.command-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.command-buttons .el-button {
  margin-left: 0;
}

.offline-alert {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .el-select {
    flex: 1;
    width: auto;
  }
}
</style>