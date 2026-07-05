<template>
  <section class="video-monitor">
    <div class="video-header">
      <div>
        <span class="section-kicker">REAL-TIME VIDEO</span>
        <strong>实时直播与飞行控制</strong>
      </div>

      <div class="control-actions">
        <el-button
          :type="streamType === 'airport' ? 'primary' : ''"
          @click="changeStream('airport')"
        >
          机场直播
        </el-button>
        <el-button
          :type="streamType === 'uav' ? 'primary' : ''"
          @click="changeStream('uav')"
        >
          无人机直播
        </el-button>
        <el-button
          type="warning"
          :loading="commandLoading"
          :disabled="!canControl"
          @click="$emit('command', 'RETURN_HOME')"
        >
          返航
        </el-button>
        <el-button
          :loading="commandLoading"
          :disabled="!canControl"
          @click="$emit('command', 'CANCEL_RETURN_HOME')"
        >
          取消返航
        </el-button>
        <el-button
          :loading="commandLoading"
          :disabled="!canControl"
          @click="$emit('command', 'PAUSE')"
        >
          暂停
        </el-button>
        <el-button
          type="success"
          :loading="commandLoading"
          :disabled="!canControl"
          @click="$emit('command', 'RESUME')"
        >
          恢复
        </el-button>
      </div>
    </div>

    <div class="stream-title">
      <span>{{ videoInfo?.streamName || '实时直播' }}</span>
      <div>
        <el-tag
          size="small"
          :type="videoInfo?.videoAvailable ? 'success' : 'warning'"
        >
          {{ videoInfo?.videoAvailable ? '接口已启用' : '接口待启用' }}
        </el-tag>
        <el-button
          type="success"
          size="small"
          :disabled="!canControl"
          @click="$emit('command', 'START_INSPECTION')"
        >
          开始检测
        </el-button>
        <el-button
          size="small"
          @click="$emit('takeover')"
        >
          人工接管
        </el-button>
      </div>
    </div>

    <div class="video-box">
      <div v-if="loading" class="video-message">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <span>正在连接直播流……</span>
      </div>

      <div v-else-if="videoInfo" class="video-placeholder">
        <span class="signal-ring" />
        <strong>{{ videoInfo.streamName }}</strong>
        <span>
          {{ videoInfo.videoAvailable ? '视频接口配置完成' : '视频接口尚未启用' }}
        </span>
        <small>
          当前使用 Mock/预留接口，接入流媒体服务器后在此播放真实画面
        </small>
      </div>

      <el-empty v-else description="暂无视频信息" />
    </div>

    <div class="stream-footer">
      <span>流地址：{{ videoInfo?.videoUrl || '未配置' }}</span>
      <span>RTSP源：{{ videoInfo?.rtspUrl || '未配置' }}</span>
      <span>数据源：{{ videoInfo?.mock ? 'Mock/预留接口' : '真实设备' }}</span>
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

import { getDroneVideo } from '@/api/droneControl'

const props = defineProps({
  deviceCode: {
    type: String,
    default: ''
  },
  canControl: {
    type: Boolean,
    default: false
  },
  commandLoading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['command', 'takeover'])

const streamType = ref('airport')
const videoInfo = ref(null)
const loading = ref(false)

async function loadVideo() {
  if (!props.deviceCode) {
    videoInfo.value = null
    return
  }

  loading.value = true

  try {
    const response = await getDroneVideo(
      props.deviceCode,
      streamType.value
    )

    if (response.code === 200) {
      videoInfo.value = response.data
    } else {
      videoInfo.value = null
      ElMessage.error(response.message)
    }
  } catch (error) {
    console.error(error)
    videoInfo.value = null
    ElMessage.error('获取视频流信息失败')
  } finally {
    loading.value = false
  }
}

async function changeStream(type) {
  if (streamType.value === type) return
  streamType.value = type
  await loadVideo()
}

watch(
  () => props.deviceCode,
  loadVideo,
  { immediate: true }
)
</script>

<style scoped>
.video-monitor {
  overflow: hidden;
  background: #ffffff;
  border: 1px solid #ebeef5;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.video-header,
.stream-title,
.stream-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.video-header {
  flex-wrap: wrap;
  padding: 16px 18px;
  border-bottom: 1px solid #ebeef5;
}

.video-header > div:first-child {
  display: grid;
  gap: 3px;
}

.section-kicker {
  color: #409eff;
  font-size: 10px;
  letter-spacing: 1.8px;
}

.video-header strong,
.stream-title {
  color: #303133;
}

.control-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.control-actions :deep(.el-button) {
  margin-left: 0;
}

.stream-title {
  padding: 12px 16px;
  background: #fafafa;
}

.stream-title > div {
  display: flex;
  gap: 8px;
}

.video-box {
  min-height: 430px;
  background:
    radial-gradient(circle at center, rgba(12, 88, 128, 0.16), transparent 36%),
    #030e20;
}

.video-message,
.video-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 13px;
  min-height: 430px;
  padding: 24px;
  color: #94b5c8;
  text-align: center;
}

.video-placeholder strong {
  color: #eafaff;
  font-size: 18px;
}

.video-placeholder small {
  max-width: 520px;
  color: #64879b;
}

.signal-ring {
  width: 44px;
  height: 44px;
  border: 3px solid rgba(14, 194, 241, 0.24);
  border-top-color: #0ec2f1;
  border-radius: 50%;
  animation: rotate 1.4s linear infinite;
}

.loading-icon {
  color: #0ec2f1;
  font-size: 40px;
  animation: rotate 1.4s linear infinite;
}

.stream-footer {
  flex-wrap: wrap;
  padding: 10px 16px;
  color: #909399;
  font-size: 12px;
  border-top: 1px solid #ebeef5;
}

@keyframes rotate {
  to { transform: rotate(360deg); }
}

@media (max-width: 900px) {
  .video-header,
  .stream-title {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
