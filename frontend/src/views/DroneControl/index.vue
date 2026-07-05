<template>
  <section class="drone-console">
    <header class="console-heading">
      <div class="heading-icon">▦</div>
      <div>
        <span class="eyebrow">UAV INSPECTION CONSOLE</span>
        <h2>无人机巡检主控台</h2>
        <p>机场设备选择、实时遥测、视频监控与飞行控制</p>
      </div>
      <div class="heading-status">
        <el-tag type="primary">数字主控台</el-tag>
        <el-tag :type="telemetry?.online ? 'success' : 'danger'">
          {{ telemetry?.online ? '设备在线' : '设备离线' }}
        </el-tag>
      </div>
    </header>

    <div class="console-grid">
      <AirportList
        :docks="docks"
        :selected-device-code="selectedDeviceCode"
        :loading="dockLoading"
        @select="handleAirportSelect"
        @refresh="loadDocks"
      />

      <VideoMonitor
        :device-code="selectedDeviceCode"
        :can-control="canControl"
        :command-loading="commandLoading"
        @command="handleCommand"
        @takeover="handleTakeover"
      />
    </div>

    <div class="information-grid">
      <section class="status-panel">
        <div class="panel-heading">
          <div>
            <span class="eyebrow">REAL-TIME TELEMETRY</span>
            <h3>飞行状态数据</h3>
          </div>
          <el-button
            type="primary"
            link
            :loading="telemetryLoading"
            @click="loadTelemetry"
          >
            刷新状态
          </el-button>
        </div>

        <div v-if="telemetry" class="telemetry-grid">
          <div class="data-tile">
            <span>设备编号</span>
            <strong>{{ telemetry.deviceCode }}</strong>
          </div>
          <div class="data-tile">
            <span>飞行状态</span>
            <strong>{{ telemetry.flightStatus }}</strong>
          </div>
          <div class="data-tile">
            <span>剩余电量</span>
            <strong>{{ telemetry.battery }}%</strong>
          </div>
          <div class="data-tile">
            <span>飞行高度</span>
            <strong>{{ telemetry.height }} m</strong>
          </div>
          <div class="data-tile">
            <span>飞行速度</span>
            <strong>{{ telemetry.speed }} m/s</strong>
          </div>
          <div class="data-tile">
            <span>当前位置</span>
            <strong>{{ telemetry.location || '--' }}</strong>
          </div>
          <div class="data-tile coordinate">
            <span>经纬度</span>
            <strong>{{ telemetry.longitude }}, {{ telemetry.latitude }}</strong>
          </div>
          <div class="data-tile coordinate">
            <span>更新时间</span>
            <strong>{{ formatTime(telemetry.updateTime) }}</strong>
          </div>
        </div>

        <el-empty v-else description="暂未获取无人机状态" />
      </section>

      <section class="safety-panel">
        <div class="panel-heading">
          <div>
            <span class="eyebrow">SAFETY ASSURANCE</span>
            <h3>安全保障与消息接入</h3>
          </div>
        </div>

        <div class="safety-list">
          <div class="safety-item">
            <span>异常安全预警</span>
            <el-tag :type="alertStatus?.level === 'normal' ? 'success' : 'danger'">
              {{ alertStatus?.status || '未知' }}
            </el-tag>
          </div>
          <div class="safety-item">
            <span>飞行合规控制</span>
            <el-tag :type="safetyStatus?.complianceStatus === '合规' ? 'success' : 'danger'">
              {{ safetyStatus?.complianceStatus || '未知' }}
            </el-tag>
          </div>
          <div class="safety-item">
            <span>禁飞区规避</span>
            <el-tag :type="safetyStatus?.inNoFlyZone ? 'danger' : 'success'">
              {{ safetyStatus?.inNoFlyZone ? '位于禁飞区' : '未进入禁飞区' }}
            </el-tag>
          </div>
          <div class="safety-item">
            <span>数据加密传输</span>
            <el-tag :type="safetyStatus?.encrypted ? 'success' : 'warning'">
              {{ safetyStatus?.encrypted ? '已加密' : '未加密' }}
            </el-tag>
          </div>
          <div class="safety-item">
            <span>EMQX消息通道</span>
            <div class="safety-actions">
              <el-tag :type="emqxStatus?.connected ? 'success' : 'warning'">
                {{ emqxStatus?.connected ? '已连接' : '接口预留' }}
              </el-tag>
              <el-button
                type="primary"
                link
                :disabled="!selectedDeviceCode"
                @click="handleEmqxSubscribe"
              >
                请求订阅
              </el-button>
            </div>
          </div>
          <div class="safety-item">
            <span>遥测数据来源</span>
            <el-tag type="primary">Mock数据</el-tag>
          </div>
        </div>
      </section>
    </div>

    <el-alert
      v-if="telemetry && !telemetry.online"
      title="当前无人机离线，飞行控制命令已禁用"
      type="warning"
      :closable="false"
      show-icon
      class="offline-alert"
    />
  </section>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import AirportList from './AirportList.vue'
import VideoMonitor from './VideoMonitor.vue'
import { getDeviceList } from '@/api/inspection'
import {
  getDockList,
  getDroneAlertStatus,
  getDroneEmqxStatus,
  getDroneSafety,
  getDroneTelemetry,
  requestDroneTakeover,
  subscribeDroneEmqx,
  sendDroneCommand
} from '@/api/droneControl'

const devices = ref([])
const docks = ref([])
const selectedDeviceCode = ref('')
const telemetry = ref(null)
const safetyStatus = ref(null)
const alertStatus = ref(null)
const emqxStatus = ref(null)
const telemetryLoading = ref(false)
const dockLoading = ref(false)
const commandLoading = ref(false)

let telemetryTimer = null
let dockTimer = null

const canControl = computed(() => {
  return Boolean(
    selectedDeviceCode.value &&
    telemetry.value?.online
  )
})

async function loadInitialData() {
  try {
    const [deviceResponse, dockResponse] = await Promise.all([
      getDeviceList(),
      getDockList()
    ])

    if (deviceResponse.code !== 200) {
      ElMessage.error(deviceResponse.message)
      return
    }

    devices.value = deviceResponse.data || []

    if (dockResponse.code === 200) {
      docks.value = dockResponse.data || []
    } else {
      ElMessage.error(dockResponse.message)
    }

    const selectableDock = docks.value.find(dock => {
      return dock.status === 'online' && dock.droneCode
    })

    const onlineDevice = devices.value.find(device => {
      return device.status === 'online'
    })

    selectedDeviceCode.value = selectableDock?.droneCode
      || onlineDevice?.code
      || devices.value[0]?.code
      || ''

    await loadDeviceStatus()
  } catch (error) {
    console.error(error)
    ElMessage.error('获取主控台初始化数据失败')
  }
}

async function loadDocks() {
  dockLoading.value = true

  try {
    const response = await getDockList()

    if (response.code === 200) {
      docks.value = response.data || []
    } else {
      ElMessage.error(response.message)
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取机场列表失败')
  } finally {
    dockLoading.value = false
  }
}

async function loadTelemetry() {
  if (!selectedDeviceCode.value) {
    telemetry.value = null
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
      telemetry.value = null
      ElMessage.error(response.message)
    }
  } catch (error) {
    console.error(error)
    telemetry.value = null
    ElMessage.error('获取无人机遥测状态失败')
  } finally {
    telemetryLoading.value = false
  }
}

async function loadDeviceStatus() {
  if (!selectedDeviceCode.value) return

  const [telemetryResult, safetyResult, alertResult, emqxResult] = await Promise.all([
    loadTelemetry(),
    getDroneSafety(selectedDeviceCode.value),
    getDroneAlertStatus(selectedDeviceCode.value),
    getDroneEmqxStatus(selectedDeviceCode.value)
  ])

  if (safetyResult.code === 200) {
    safetyStatus.value = safetyResult.data
  }

  if (alertResult.code === 200) {
    alertStatus.value = alertResult.data
  }

  if (emqxResult.code === 200) {
    emqxStatus.value = emqxResult.data
  }

  return telemetryResult
}

async function handleAirportSelect(deviceCode) {
  if (!deviceCode || deviceCode === selectedDeviceCode.value) return
  selectedDeviceCode.value = deviceCode
  telemetry.value = null
  safetyStatus.value = null
  alertStatus.value = null
  emqxStatus.value = null
  await loadDeviceStatus()
}

async function handleCommand(command) {
  if (!canControl.value) {
    ElMessage.warning('当前设备离线或尚未选择无人机')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确认向设备 ${selectedDeviceCode.value} 发送控制命令吗？`,
      '飞行控制确认',
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

async function handleTakeover() {
  if (!selectedDeviceCode.value) return

  try {
    const response = await requestDroneTakeover(
      selectedDeviceCode.value
    )
    if (response.code === 200) {
      ElMessage.info(response.data.message)
    } else {
      ElMessage.error(response.message)
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('请求人工接管接口失败')
  }
}

async function handleEmqxSubscribe() {
  if (!selectedDeviceCode.value) return

  try {
    const response = await subscribeDroneEmqx(
      selectedDeviceCode.value
    )
    if (response.code === 200) {
      emqxStatus.value = response.data
      ElMessage.info(response.data.message)
    } else {
      ElMessage.error(response.message)
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('请求EMQX订阅接口失败')
  }
}

function formatTime(timestamp) {
  if (!timestamp) return '--'
  return new Date(timestamp).toLocaleString()
}

onMounted(async () => {
  await loadInitialData()
  telemetryTimer = window.setInterval(loadTelemetry, 5000)
  dockTimer = window.setInterval(loadDocks, 10000)
})

onUnmounted(() => {
  window.clearInterval(telemetryTimer)
  window.clearInterval(dockTimer)
})
</script>

<style scoped>
.drone-console {
  min-height: 100%;
  color: #303133;
}

.console-heading,
.heading-status,
.panel-heading {
  display: flex;
  align-items: center;
}

.console-heading {
  gap: 14px;
  margin-bottom: 18px;
  padding: 16px 20px;
  background: #ffffff;
  border: 1px solid #ebeef5;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.heading-icon {
  display: grid;
  width: 44px;
  height: 44px;
  color: #eafaff;
  font-size: 25px;
  place-items: center;
  background: #409eff;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.28);
}

.console-heading h2,
.panel-heading h3 {
  margin: 3px 0;
}

.console-heading p {
  margin: 0;
  color: #909399;
}

.heading-status {
  gap: 8px;
  margin-left: auto;
}

.eyebrow {
  color: #409eff;
  font-size: 10px;
  letter-spacing: 1.8px;
}

.console-grid {
  display: grid;
  grid-template-columns: minmax(310px, 360px) minmax(0, 1fr);
  gap: 16px;
}

.information-grid {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(300px, 1fr);
  gap: 16px;
  margin-top: 16px;
}

.status-panel,
.safety-panel {
  padding: 18px;
  background: #ffffff;
  border: 1px solid #ebeef5;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.panel-heading {
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 15px;
}

.telemetry-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.data-tile {
  display: grid;
  gap: 6px;
  min-height: 64px;
  padding: 12px;
  background: #fafafa;
  border: 1px solid #ebeef5;
  border-radius: 8px;
}

.data-tile span {
  color: #909399;
  font-size: 12px;
}

.data-tile strong {
  overflow: hidden;
  color: #303133;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.data-tile.coordinate {
  grid-column: span 2;
}

.safety-list {
  display: grid;
  gap: 10px;
}

.safety-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  color: #606266;
  background: #fafafa;
  border: 1px solid #ebeef5;
  border-radius: 7px;
}

.safety-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.offline-alert {
  margin-top: 16px;
}

@media (max-width: 820px) {
  .console-grid,
  .information-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .console-heading {
    align-items: flex-start;
    flex-wrap: wrap;
  }

  .heading-status {
    width: 100%;
    margin-left: 0;
  }

  .telemetry-grid {
    grid-template-columns: 1fr 1fr;
  }

  .data-tile.coordinate {
    grid-column: span 2;
  }
}
</style>
