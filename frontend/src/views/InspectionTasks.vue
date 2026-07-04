<template>
  <section class="inspection-tasks">
    <div class="page-header">
      <div>
        <h2>巡检任务管理</h2>
        <p>管理和监控无人机巡检任务执行情况</p>
      </div>
      <el-button type="primary" :loading="loading" @click="refreshTasks">刷新任务</el-button>
    </div>

    <el-row :gutter="16" class="stat-row">
      <el-col v-for="item in stats" :key="item.label" :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="never">
          <div class="stat-value">{{ item.value }}</div>
          <div class="stat-label">{{ item.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <section class="screen-panel">
      <div class="panel-title">
        <span>巡检任务大屏</span>
        <el-tag type="info">点击详情查看完整流程</el-tag>
      </div>
      <div class="command-screen">
        <div class="map-panel">
          <div class="route-line"></div>
          <div class="route-node node-start">站</div>
          <div class="route-node node-mid"></div>
          <div class="route-node node-end"></div>
          <div class="map-label label-a">太子河</div>
          <div class="map-label label-b">阳王村</div>
          <div class="map-label label-c">巡检航线</div>
        </div>
        <div class="screen-side">
          <div class="screen-card">
            <div class="screen-card-title">
              <span>AI检测</span>
              <el-button link type="primary" @click="goDetail(featuredTask.id)">详情</el-button>
            </div>
            <div class="ai-preview">
              <div class="pipe pipe-left"></div>
              <div class="pipe pipe-right"></div>
              <span>异常锈蚀段</span>
            </div>
            <p>AI检测发现：{{ featuredDefect.type }}</p>
            <small>{{ featuredTask.createdTime }}</small>
          </div>
          <div class="screen-card">
            <div class="screen-card-title">
              <span>巡检任务</span>
              <el-button link type="primary" @click="goDetail(featuredTask.id)">详情</el-button>
            </div>
            <div class="mini-table mini-head">
              <span>巡检类型</span>
              <span>巡检状态</span>
              <span>巡检时间</span>
            </div>
            <div v-for="task in filteredTasks.slice(0, 5)" :key="task.id" class="mini-table">
              <span>轨道检测</span>
              <el-tag size="small" :type="statusType(task.status)">{{ statusLabel(task.status) }}</el-tag>
              <span>{{ task.createdTime.slice(0, 10) }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <el-card class="panel">
      <template #header>
        <div class="table-header">
          <span>巡检任务列表</span>
          <div class="filters">
            <el-input v-model="keyword" clearable placeholder="搜索任务ID、航线名称..." />
            <el-select v-model="statusFilter" clearable placeholder="全部状态">
              <el-option label="待检测" value="pending" />
              <el-option label="扫描中" value="running" />
              <el-option label="已完成" value="completed" />
              <el-option label="异常" value="abnormal" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table :data="filteredTasks" border style="width: 100%" empty-text="暂无巡检任务">
        <el-table-column prop="code" label="任务编号" min-width="150" />
        <el-table-column prop="name" label="任务名称" min-width="220" />
        <el-table-column prop="routeName" label="巡检线路/区域" min-width="180" />
        <el-table-column prop="createdTime" label="创建时间" min-width="170" />
        <el-table-column prop="status" label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="160">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :status="progressStatus(row.status)" />
          </template>
        </el-table-column>
        <el-table-column prop="cleanStatus" label="已清理" width="110" />
        <el-table-column label="操作" width="190" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" type="primary" plain @click="goDetail(row.id)">详情</el-button>
            <el-button size="small" type="success" plain @click="mockClean(row)">清理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <section class="result-panel">
      <div class="result-toolbar">
        <el-input v-model="keyword" clearable placeholder="搜索任务ID、航线名称..." />
        <el-select v-model="statusFilter" placeholder="全部状态" clearable>
          <el-option label="待检测" value="pending" />
          <el-option label="扫描中" value="running" />
          <el-option label="已完成" value="completed" />
          <el-option label="异常" value="abnormal" />
        </el-select>
        <el-select v-model="cleanFilter" placeholder="全部处理" clearable>
          <el-option label="未清理" value="未清理" />
          <el-option label="待清理" value="待清理" />
          <el-option label="已清理" value="已清理" />
        </el-select>
        <el-button type="primary" @click="resetFilters">重置筛选</el-button>
      </div>
      <div class="result-table">
        <div class="result-row result-head">
          <span>巡检任务名</span>
          <span>创建时间</span>
          <span>状态</span>
          <span>已清理</span>
          <span>操作</span>
        </div>
        <div v-for="task in filteredTasks" :key="`result-${task.id}`" class="result-row">
          <span>{{ task.code || task.name }}</span>
          <span>{{ task.createdTime }}</span>
          <span><el-tag size="small" :type="statusType(task.status)">{{ statusLabel(task.status) }}</el-tag></span>
          <span><el-tag size="small" type="info">{{ task.cleanStatus || '未清理' }}</el-tag></span>
          <span class="result-actions">
            <el-button size="small" type="primary" @click="goDetail(task.id)">统计</el-button>
            <el-button size="small" type="warning" @click="goDetail(task.id)">任务列表</el-button>
            <el-button size="small" type="success" @click="mockClean(task)">清理</el-button>
          </span>
        </div>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getInspectionList, getMockInspectionList } from '@/api/inspection'

const router = useRouter()
const tasks = ref([])
const loading = ref(false)
const keyword = ref('')
const statusFilter = ref('')
const cleanFilter = ref('')

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

const formatTime = (value) => {
  if (!value) return ''
  return String(value).replace('T', ' ').slice(0, 19)
}

const normalizeTask = (task) => {
  const device = task.device || {}
  const status = normalizeStatus(task.status)
  return {
    ...task,
    status,
    code: task.code || task.task_code || `TASK-${String(task.id).padStart(4, '0')}`,
    name: task.name || task.task_name || '城市轨道巡检任务',
    routeName: task.routeName || task.route_name || task.description || '城市轨道交通巡检区域',
    areaName: task.areaName || task.area_name || '巡检区域',
    deviceName: task.deviceName || task.device_name || device.name || '',
    pilot: task.pilot || task.owner || '巡检管理员',
    cleanStatus: task.cleanStatus || task.clean_status || (status === 'completed' ? '已清理' : '未清理'),
    createdTime: formatTime(task.createdTime || task.created_time || task.created_at),
    startTime: formatTime(task.startTime || task.start_time),
    endTime: formatTime(task.endTime || task.end_time),
    progress: Number(task.progress || (status === 'completed' ? 100 : status === 'running' ? 60 : 0))
  }
}

const refreshTasks = async () => {
  loading.value = true
  try {
    const data = await getInspectionList()
    const list = Array.isArray(data) ? data : []
    tasks.value = list.length ? list.map(normalizeTask) : (await getMockInspectionList()).map(normalizeTask)
  } catch (error) {
    tasks.value = (await getMockInspectionList()).map(normalizeTask)
    ElMessage.warning('后端巡检任务接口暂不可用，已加载本地模拟数据')
  } finally {
    loading.value = false
  }
}

const filteredTasks = computed(() => {
  const key = keyword.value.trim()
  return tasks.value.filter(task => {
    const matchKeyword = !key || [task.name, task.code, task.routeName, task.areaName].some(value => String(value || '').includes(key))
    const matchStatus = !statusFilter.value || task.status === statusFilter.value
    const matchClean = !cleanFilter.value || task.cleanStatus === cleanFilter.value
    return matchKeyword && matchStatus && matchClean
  })
})

const featuredTask = computed(() => filteredTasks.value[0] || tasks.value[0] || {})
const featuredDefect = computed(() => featuredTask.value.defects?.[0] || { type: '疑似异常' })

const stats = computed(() => [
  { label: '任务总数', value: tasks.value.length },
  { label: '扫描中', value: tasks.value.filter(item => item.status === 'running').length },
  { label: '异常任务', value: tasks.value.filter(item => ['abnormal', 'failed'].includes(item.status)).length },
  { label: '平均进度', value: `${Math.round(tasks.value.reduce((sum, item) => sum + item.progress, 0) / (tasks.value.length || 1))}%` }
])

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

const goDetail = (id) => {
  if (!id) return
  router.push(`/inspection-tasks/${id}`)
}

const mockClean = (task) => {
  task.cleanStatus = '已清理'
  ElMessage.success('任务数据清理状态已更新')
}

const resetFilters = () => {
  keyword.value = ''
  statusFilter.value = ''
  cleanFilter.value = ''
}

onMounted(refreshTasks)
</script>

<style scoped>
.inspection-tasks {
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

.stat-row,
.panel,
.screen-panel,
.result-panel {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 8px;
}

.stat-value {
  color: #303133;
  font-size: 28px;
  font-weight: 700;
}

.stat-label {
  margin-top: 8px;
  color: #909399;
}

.screen-panel,
.result-panel {
  padding: 18px;
  border: 1px solid #0d4b8f;
  border-radius: 8px;
  background: #061a36;
}

.panel-title,
.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.panel-title {
  margin-bottom: 16px;
  color: #d7ecff;
  font-size: 18px;
  font-weight: 700;
}

.command-screen {
  display: grid;
  grid-template-columns: minmax(320px, 1.1fr) minmax(320px, 0.95fr);
  gap: 18px;
}

.map-panel {
  position: relative;
  min-height: 470px;
  overflow: hidden;
  border: 1px solid #0a63b7;
  border-radius: 8px;
  background:
    linear-gradient(120deg, rgba(18, 94, 60, 0.5), rgba(14, 41, 70, 0.45)),
    repeating-linear-gradient(35deg, rgba(255, 255, 255, 0.06) 0 2px, transparent 2px 70px),
    repeating-linear-gradient(105deg, rgba(255, 218, 95, 0.16) 0 3px, transparent 3px 88px),
    #1b4d51;
}

.route-line {
  position: absolute;
  left: 16%;
  top: 24%;
  width: 68%;
  height: 130px;
  border-top: 5px solid #ff4fd2;
  border-right: 5px solid #ff4fd2;
  border-radius: 28px 72px 0 0;
  transform: rotate(-12deg);
  box-shadow: 0 0 14px rgba(255, 79, 210, 0.85);
}

.route-node {
  position: absolute;
  width: 22px;
  height: 22px;
  border: 3px solid #ffcb4b;
  border-radius: 50%;
  background: #ff6b35;
  box-shadow: 0 0 12px rgba(255, 203, 75, 0.8);
}

.node-start {
  left: 12%;
  top: 28%;
  width: 58px;
  height: 58px;
  display: grid;
  place-items: center;
  color: #eafff3;
  font-weight: 700;
  background: #20d47a;
}

.node-mid {
  left: 45%;
  top: 19%;
}

.node-end {
  right: 9%;
  top: 16%;
}

.map-label {
  position: absolute;
  color: #eef8ff;
  font-weight: 700;
  text-shadow: 0 1px 4px #001226;
}

.label-a { left: 9%; top: 55%; }
.label-b { left: 15%; top: 64%; }
.label-c { right: 12%; top: 40%; }

.screen-side {
  display: grid;
  gap: 18px;
}

.screen-card {
  padding: 16px;
  color: #d7ecff;
  border: 1px solid #0a63b7;
  border-radius: 8px;
  background: linear-gradient(180deg, rgba(0, 61, 127, 0.85), rgba(3, 24, 55, 0.95));
}

.screen-card-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  font-size: 20px;
  font-weight: 700;
}

.ai-preview {
  position: relative;
  height: 170px;
  overflow: hidden;
  border-radius: 8px;
  background: linear-gradient(180deg, #d8c3aa, #9f8269);
}

.pipe {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 58px;
  background: linear-gradient(90deg, #c9c9c9, #f4f4f4, #a8a8a8);
}

.pipe-left { left: 26%; }
.pipe-right { right: 28%; }

.ai-preview span {
  position: absolute;
  left: 18px;
  bottom: 12px;
  padding: 3px 8px;
  color: #fff;
  border-radius: 4px;
  background: rgba(26, 180, 82, 0.92);
}

.screen-card p {
  margin: 14px 0 4px;
  font-weight: 700;
}

.screen-card small {
  color: #9fb9d8;
}

.mini-table {
  display: grid;
  grid-template-columns: 1fr 96px 110px;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  color: #d7ecff;
}

.mini-head {
  color: #7ed7ff;
  border: 1px solid #0b72c9;
  border-radius: 4px;
  background: rgba(0, 116, 203, 0.35);
}

.filters {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) 150px;
  gap: 12px;
}

.result-toolbar {
  display: grid;
  grid-template-columns: minmax(280px, 1fr) 160px 160px 110px;
  gap: 14px;
  margin-bottom: 16px;
}

.result-table {
  overflow: hidden;
  border: 1px solid #0a3568;
  border-radius: 8px;
}

.result-row {
  min-height: 48px;
  display: grid;
  grid-template-columns: 1.25fr 1.1fr 0.6fr 0.6fr 1.2fr;
  align-items: center;
  gap: 12px;
  padding: 0 14px;
  color: #d8e9ff;
  background: rgba(3, 25, 58, 0.92);
  border-bottom: 1px solid rgba(26, 84, 145, 0.45);
}

.result-head {
  min-height: 44px;
  color: #32b8ff;
  font-weight: 700;
  background: rgba(8, 59, 114, 0.95);
}

.result-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

@media (max-width: 768px) {
  .page-header,
  .panel-title,
  .table-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .command-screen,
  .filters,
  .result-toolbar,
  .result-row {
    grid-template-columns: 1fr;
  }
}
</style>
