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
          <div>
            <el-button type="success" plain @click="openTaskDialog()">
              <el-icon><Plus /></el-icon> 新增任务
            </el-button>
            <el-button type="primary" plain @click="loadData">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="taskData" v-loading="loading" border stripe style="width: 100%">
        <el-table-column prop="id" label="任务ID" width="80" />
        <el-table-column prop="name" label="任务名称" min-width="160" />
        <el-table-column prop="device_name" label="执行设备" min-width="120">
          <template #default="{ row }">{{ row.device_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="area" label="巡检区域" min-width="120">
          <template #default="{ row }">{{ row.area || '-' }}</template>
        </el-table-column>
        <el-table-column prop="status_display" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ row.status_display || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :stroke-width="10" />
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="180" align="center">
          <template #default="{ row }">
            <el-button size="small" type="primary" plain @click="openTaskDialog(row)">
              <el-icon><Edit /></el-icon> 修改
            </el-button>
            <el-button size="small" type="danger" plain @click="handleDeleteTask(row)">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 任务 新增/编辑 弹窗 -->
    <el-dialog
      v-model="taskDialogVisible"
      :title="editingTask ? '编辑巡检任务' : '新增巡检任务'"
      width="520px"
      destroy-on-close
    >
      <el-form
        ref="taskFormRef"
        :model="taskForm"
        :rules="taskRules"
        label-width="90px"
      >
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="执行设备" prop="device">
          <el-select v-model="taskForm.device" placeholder="请选择设备" clearable style="width: 100%">
            <el-option
              v-for="d in deviceList"
              :key="d.id"
              :label="d.name"
              :value="d.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="巡检区域" prop="area">
          <el-input v-model="taskForm.area" placeholder="请输入巡检区域" />
        </el-form-item>
        <el-form-item label="任务状态" prop="status">
          <el-select v-model="taskForm.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="待执行" value="pending" />
            <el-option label="执行中" value="running" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="taskForm.priority" placeholder="请选择优先级" style="width: 100%">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
          </el-select>
        </el-form-item>
        <el-form-item label="进度" prop="progress">
          <el-slider v-model="taskForm.progress" :max="100" show-input />
        </el-form-item>
        <el-form-item label="任务描述" prop="description">
          <el-input v-model="taskForm.description" type="textarea" :rows="3" placeholder="请输入任务描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="taskDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="taskSubmitting" @click="handleSubmitTask">确定</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import {
  getInspectionList,
  getOverview,
  createInspection,
  updateInspection,
  deleteInspection,
  getDeviceList
} from '@/api/inspection'

const loading = ref(false)

const overview = reactive({
  totalTasks: 4,
  activeTasks: 2,
  onlineDevices: 2
})

const taskData = ref([])

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
    taskData.value = Array.isArray(taskResponse.data) ? taskResponse.data : (taskResponse.data?.results || [])
  } catch {
    // Keep empty when backend is not running
  } finally {
    loading.value = false
  }
}

// ── 任务弹窗 ─────────────────────────────────────────────

const taskDialogVisible = ref(false)
const editingTask = ref(null)
const taskFormRef = ref(null)
const taskSubmitting = ref(false)
const deviceList = ref([])

const taskForm = reactive({
  name: '',
  device: null,
  area: '',
  status: 'pending',
  priority: 'medium',
  progress: 0,
  description: ''
})

const taskRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  area: [{ required: true, message: '请输入巡检区域', trigger: 'blur' }]
}

const loadDevices = async () => {
  try {
    const res = await getDeviceList()
    deviceList.value = Array.isArray(res.data) ? res.data : (res.data?.results || [])
  } catch {
    deviceList.value = []
  }
}

const openTaskDialog = async (editing = null) => {
  editingTask.value = editing
  await loadDevices()

  if (editing) {
    Object.assign(taskForm, {
      name: editing.name || '',
      device: editing.device || null,
      area: editing.area || '',
      status: editing.status || 'pending',
      priority: editing.priority || 'medium',
      progress: editing.progress || 0,
      description: editing.description || ''
    })
  } else {
    Object.assign(taskForm, {
      name: '', device: null, area: '', status: 'pending', priority: 'medium', progress: 0, description: ''
    })
  }
  taskDialogVisible.value = true
}

const handleSubmitTask = async () => {
  if (!taskFormRef.value) return
  try { await taskFormRef.value.validate() } catch { return }

  taskSubmitting.value = true
  try {
    const payload = { ...taskForm }
    if (!payload.device) delete payload.device

    if (editingTask.value) {
      await updateInspection(editingTask.value.id, payload)
      ElMessage.success('任务修改完成')
    } else {
      await createInspection(payload)
      ElMessage.success('任务新增完成')
    }
    taskDialogVisible.value = false
    loadData()
  } catch (err) {
    ElMessage.error(err.message || '操作失败')
  } finally {
    taskSubmitting.value = false
  }
}

const handleDeleteTask = (row) => {
  ElMessageBox.confirm(`确定要删除任务「${row.name}」吗？`, '删除确认', {
    type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消'
  }).then(async () => {
    try {
      await deleteInspection(row.id)
      ElMessage.success('任务删除完成')
      loadData()
    } catch (err) {
      ElMessage.error(err.message || '删除失败')
    }
  }).catch(() => {})
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
