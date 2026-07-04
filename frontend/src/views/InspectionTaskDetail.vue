<template>
  <section v-if="task" class="task-detail">
    <div class="page-header">
      <div>
        <el-button link type="primary" @click="router.push('/inspection-tasks')">返回巡检任务</el-button>
        <h2>{{ task.name }}</h2>
        <p>{{ task.description }}</p>
      </div>
      <el-tag size="large" :type="statusType(task.status)">{{ statusLabel(task.status) }}</el-tag>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :md="16">
        <el-card shadow="never" class="panel">
          <template #header>任务执行流程</template>
          <el-steps :active="activeStep" finish-status="success" align-center>
            <el-step v-for="step in task.steps" :key="step.title" :title="step.title" :description="step.time" :status="step.status" />
          </el-steps>
        </el-card>

        <el-card shadow="never" class="panel">
          <template #header>实时直播与文件接入</template>
          <div class="video-area">
            <div class="video-placeholder">
              <span>RTSP</span>
              <strong>视频流预留区域</strong>
              <p>{{ task.rtspUrl }}</p>
            </div>
            <div class="file-note">
              <h3>本地文件服务</h3>
              <p>巡检图片、视频和报告通过本地 Python 上传服务接收，再以静态文件地址访问，不依赖 MinIO。</p>
              <code>python tools/local-file-server.py</code>
            </div>
          </div>
        </el-card>

        <el-card shadow="never" class="panel">
          <template #header>巡检文件上传</template>
          <el-upload
            drag
            multiple
            name="file"
            :action="uploadUrl"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :file-list="uploadedFiles"
          >
            <div class="upload-text">
              <strong>拖拽巡检图片、视频或报告到此处</strong>
              <span>文件会上传到本地 Python 服务，并返回可访问的静态 URL</span>
            </div>
          </el-upload>
          <el-table :data="uploadedFiles" class="upload-table" empty-text="暂无已上传文件">
            <el-table-column prop="name" label="文件名" min-width="180" />
            <el-table-column prop="url" label="访问地址" min-width="260">
              <template #default="{ row }">
                <a v-if="row.url" :href="row.url" target="_blank">{{ row.url }}</a>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card shadow="never" class="panel">
          <template #header>缺陷与告警关联</template>
          <el-table :data="task.defects" empty-text="当前任务暂无缺陷记录" style="width: 100%">
            <el-table-column prop="id" label="编号" width="100" />
            <el-table-column prop="type" label="类型" min-width="140" />
            <el-table-column prop="position" label="位置" min-width="200" />
            <el-table-column prop="level" label="等级" width="90">
              <template #default="{ row }">
                <el-tag :type="row.level === '高' ? 'danger' : row.level === '中' ? 'warning' : 'info'">{{ row.level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="处理状态" width="120" />
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="8">
        <el-card shadow="never" class="panel">
          <template #header>任务基本信息</template>
          <dl class="info-list">
            <div><dt>任务编号</dt><dd>{{ task.code }}</dd></div>
            <div><dt>巡检线路</dt><dd>{{ task.routeName }}</dd></div>
            <div><dt>巡检区域</dt><dd>{{ task.areaName }}</dd></div>
            <div><dt>执行设备</dt><dd>{{ task.deviceName }}</dd></div>
            <div><dt>负责人</dt><dd>{{ task.pilot }}</dd></div>
            <div><dt>创建时间</dt><dd>{{ task.createdTime }}</dd></div>
            <div><dt>开始时间</dt><dd>{{ task.startTime || '-' }}</dd></div>
            <div><dt>结束时间</dt><dd>{{ task.endTime || '-' }}</dd></div>
          </dl>
        </el-card>

        <el-card shadow="never" class="panel">
          <template #header>巡检成果统计</template>
          <div class="result-grid">
            <div><strong>{{ task.resultSummary.photos }}</strong><span>图片</span></div>
            <div><strong>{{ task.resultSummary.videos }}</strong><span>视频</span></div>
            <div><strong>{{ task.resultSummary.defects }}</strong><span>缺陷</span></div>
            <div><strong>{{ task.resultSummary.warnings }}</strong><span>告警</span></div>
          </div>
          <el-progress :percentage="task.progress" :status="progressStatus(task.status)" />
        </el-card>

        <el-card shadow="never" class="panel">
          <template #header>操作记录</template>
          <el-timeline>
            <el-timeline-item v-for="log in task.logs" :key="log" :timestamp="log.slice(0, 5)">
              {{ log.slice(6) || log }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getInspectionDetail, getMockInspectionDetail } from '@/api/inspection'

const route = useRoute()
const router = useRouter()
const task = ref(null)
const uploadUrl = 'http://127.0.0.1:8000/upload'
const uploadedFiles = ref([])

const statusMap = {
  pending: '待检测',
  running: '扫描中',
  completed: '已完成',
  abnormal: '异常',
  failed: '异常',
  待执行: '待检测',
  执行中: '扫描中',
  已完成: '已完成',
  异常: '异常'
}

const normalizeStatus = (status) => {
  if (['pending', 'running', 'completed', 'abnormal', 'failed'].includes(status)) return status
  const reverse = { 待执行: 'pending', 待检测: 'pending', 扫描中: 'running', 执行中: 'running', 已完成: 'completed', 异常: 'abnormal' }
  return reverse[status] || status || 'pending'
}

const activeStep = computed(() => {
  if (!task.value?.steps) return 0
  const processIndex = task.value.steps.findIndex(item => item.status === 'process' || item.status === 'error')
  if (processIndex >= 0) return processIndex + 1
  return task.value.steps.filter(item => item.status === 'success').length
})

const formatTime = (value) => {
  if (!value) return ''
  return String(value).replace('T', ' ').slice(0, 19)
}

const buildSteps = (status) => {
  const normalized = normalizeStatus(status)
  const successCount = normalized === 'completed' ? 6 : normalized === 'running' ? 4 : ['abnormal', 'failed'].includes(normalized) ? 4 : 1
  return ['任务创建', '任务下发', '无人机起飞', '巡检执行', '结果回传', '任务完成'].map((title, index) => ({
    title,
    time: index < successCount ? '已完成' : '--',
    status: ['abnormal', 'failed'].includes(normalized) && index === 3 ? 'error' : index < successCount ? 'success' : 'wait'
  }))
}

const normalizeTask = (data) => {
  const device = data.device || {}
  const status = normalizeStatus(data.status)
  return {
    ...data,
    status,
    code: data.code || data.task_code || `TASK-${String(data.id).padStart(4, '0')}`,
    name: data.name || data.task_name || '城市轨道巡检任务',
    routeName: data.routeName || data.route_name || data.description || '城市轨道交通巡检区域',
    areaName: data.areaName || data.area_name || '巡检区域',
    deviceName: data.deviceName || data.device_name || device.name || `设备 ${data.device_id || '-'}`,
    pilot: data.pilot || data.owner || '巡检管理员',
    cleanStatus: data.cleanStatus || data.clean_status || '未清理',
    createdTime: formatTime(data.createdTime || data.created_time || data.created_at),
    startTime: formatTime(data.startTime || data.start_time),
    endTime: formatTime(data.endTime || data.end_time),
    rtspUrl: data.rtspUrl || data.rtsp_url || device.rtsp_url || 'rtsp://127.0.0.1:8554/uav-preview',
    resultSummary: data.resultSummary || { photos: 0, videos: 0, defects: 0, warnings: 0 },
    steps: data.steps || buildSteps(status),
    defects: data.defects || [],
    logs: data.logs || ['任务信息已加载，等待执行记录回传'],
    progress: Number(data.progress || (status === 'completed' ? 100 : status === 'running' ? 60 : 0))
  }
}

const loadTask = async () => {
  try {
    const data = await getInspectionDetail(route.params.id)
    task.value = normalizeTask(data)
  } catch (error) {
    const data = await getMockInspectionDetail(route.params.id)
    task.value = normalizeTask(data)
    ElMessage.warning('后端任务详情暂不可用，已加载本地模拟数据')
  }
}

const statusLabel = (status) => statusMap[status] || status || '待检测'

const statusType = (status) => {
  const map = { pending: 'warning', running: 'primary', completed: 'success', abnormal: 'danger', failed: 'danger' }
  return map[status] || 'info'
}

const progressStatus = (status) => {
  if (status === 'completed') return 'success'
  if (['abnormal', 'failed'].includes(status)) return 'exception'
  return ''
}

const handleUploadSuccess = (response, file) => {
  const data = response?.data || {}
  uploadedFiles.value.push({
    name: data.name || file.name,
    url: data.url || ''
  })
  ElMessage.success('文件上传成功')
}

const handleUploadError = () => {
  ElMessage.error('文件上传失败，请先运行 python tools/local-file-server.py')
}

onMounted(loadTask)
</script>

<style scoped>
.task-detail {
  width: 100%;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 10px 0;
}

.page-header p {
  margin: 0;
  color: #909399;
  line-height: 1.7;
}

.panel {
  margin-bottom: 16px;
}

.video-area {
  display: grid;
  grid-template-columns: minmax(260px, 1.4fr) minmax(220px, 0.8fr);
  gap: 16px;
}

.video-placeholder {
  min-height: 260px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #ffffff;
  text-align: center;
  border-radius: 8px;
  background: #1d1e1f;
}

.video-placeholder span {
  color: #67c23a;
  font-weight: 700;
}

.video-placeholder p {
  margin: 0;
  color: #cfd8e3;
}

.file-note {
  padding: 16px;
  border-radius: 8px;
  background: #f5f7fa;
}

.file-note h3 {
  margin: 0 0 10px;
}

.file-note p {
  margin-bottom: 12px;
  color: #606266;
  line-height: 1.7;
}

.file-note code {
  display: block;
  padding: 10px;
  color: #303133;
  border-radius: 6px;
  background: #ffffff;
}

.upload-text {
  display: grid;
  gap: 8px;
  color: #303133;
}

.upload-text span {
  color: #909399;
}

.upload-table {
  margin-top: 16px;
}

.info-list {
  display: grid;
  gap: 12px;
  margin: 0;
}

.info-list div {
  display: grid;
  grid-template-columns: 86px 1fr;
  gap: 12px;
}

.info-list dt {
  color: #909399;
}

.info-list dd {
  margin: 0;
  color: #303133;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.result-grid div {
  padding: 14px;
  text-align: center;
  border-radius: 8px;
  background: #f8fbff;
}

.result-grid strong {
  display: block;
  color: #303133;
  font-size: 24px;
}

.result-grid span {
  color: #909399;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
  }

  .video-area {
    grid-template-columns: 1fr;
  }
}
</style>
