<template>
  <div class="alert-manage">
    <!-- 搜索筛选区域 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="告警内容">
          <el-input v-model="filterForm.search" placeholder="输入告警描述/航线名称" clearable />
        </el-form-item>
        <el-form-item label="处理状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已解决" value="resolved" />
            <el-option label="已忽略" value="ignored" />
          </el-select>
        </el-form-item>
        <el-form-item label="检测类型">
          <el-select v-model="filterForm.detect_type" placeholder="全部类型" clearable>
            <el-option label="障碍物" value="obstacle" />
            <el-option label="缺陷" value="defect" />
            <el-option label="异常行为" value="anomaly" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
          <el-button type="success" @click="handleCreate">新增告警</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 告警列表 -->
    <el-card class="table-card">
      <el-table :data="alertList" border style="width: 100%" v-loading="loading">
        <el-table-column prop="route_name" label="航线名称" min-width="120" />
        <el-table-column prop="alert_time" label="告警时间" min-width="160" sortable>
          <template #default="{ row }">
            {{ new Date(row.alert_time).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="detect_type" label="检测类型" min-width="100">
          <template #default="{ row }">
            <el-tag :type="detectTypeTag(row.detect_type)" size="small">
              {{ detectTypeLabel(row.detect_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="告警描述" min-width="150" show-overflow-tooltip />
        <el-table-column prop="location" label="位置信息" min-width="120" />
        <el-table-column prop="status" label="处理状态" min-width="100">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="handleView(row)">查看</el-button>
            <el-button type="text" size="small" @click="handleEdit(row)">更新</el-button>
            <el-button type="text" size="small" style="color: #f56c6c" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSearch"
          @current-change="handleSearch"
        />
      </div>
    </el-card>

    <!-- 查看/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" label-width="100px" ref="formRef" :rules="formRules">
        <el-form-item label="航线名称" prop="route_name">
          <el-input v-model="formData.route_name" placeholder="请输入航线名称" />
        </el-form-item>
        <el-form-item label="检测类型" prop="detect_type">
          <el-select v-model="formData.detect_type" placeholder="请选择">
            <el-option label="障碍物" value="obstacle" />
            <el-option label="缺陷" value="defect" />
            <el-option label="异常行为" value="anomaly" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="告警描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入详细描述" />
        </el-form-item>
        <el-form-item label="位置信息" prop="location">
          <el-input v-model="formData.location" placeholder="请输入位置" />
        </el-form-item>
        <el-form-item label="处理状态" prop="status">
          <el-select v-model="formData.status" placeholder="请选择">
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已解决" value="resolved" />
            <el-option label="已忽略" value="ignored" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="formData.remark" placeholder="备注信息（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getAlertList,
  createAlert,
  updateAlert,
  deleteAlert,
  getAlertDetail
} from '@/api/alert'  


const filterForm = reactive({
  search: '',
  status: '',
  detect_type: '',
  dateRange: [],
})


const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
})


const alertList = ref([])
const loading = ref(false)


const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false) 
const formData = reactive({
  id: undefined,
  route_name: '',
  detect_type: 'other',
  description: '',
  location: '',
  status: 'pending',
  remark: '',
})
const formRef = ref(null)
const formRules = {
  route_name: [{ required: true, message: '请输入航线名称', trigger: 'blur' }],
  detect_type: [{ required: true, message: '请选择检测类型', trigger: 'change' }],
  description: [{ required: true, message: '请输入告警描述', trigger: 'blur' }],
  location: [{ required: true, message: '请输入位置信息', trigger: 'blur' }],
  status: [{ required: true, message: '请选择处理状态', trigger: 'change' }],
}


const fetchAlerts = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      search: filterForm.search || undefined,
      status: filterForm.status || undefined,
      detect_type: filterForm.detect_type || undefined,
    }
    
    const res = await getAlertList(params)
   
    if (res.data && res.data.results) {
      alertList.value = res.data.results
      pagination.total = res.data.count
    } else {
      
      alertList.value = res.data
      pagination.total = res.data.length
    }
  } catch (error) {
    ElMessage.error('获取告警列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}


const handleSearch = () => {
  pagination.page = 1
  fetchAlerts()
}


const resetSearch = () => {
  filterForm.search = ''
  filterForm.status = ''
  filterForm.detect_type = ''
  filterForm.dateRange = []
  handleSearch()
}


const handleCreate = () => {
  isEdit.value = false
  dialogTitle.value = '新增告警'
  
  Object.assign(formData, {
    id: undefined,
    route_name: '',
    detect_type: 'other',
    description: '',
    location: '',
    status: 'pending',
    remark: '',
  })
  dialogVisible.value = true
}


const handleView = (row) => {
  isEdit.value = false 
  dialogTitle.value = '查看告警详情'
  
  Object.assign(formData, { ...row })
  
  ElMessage.info(`告警详情：${row.description}，位置：${row.location}`)
}


const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑告警'
  
  Object.assign(formData, { ...row })
  dialogVisible.value = true
}


const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除告警“${row.route_name}”吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteAlert(row.id)
      ElMessage.success('删除成功')
      fetchAlerts()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}


const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  try {
    if (isEdit.value) {
      
      await updateAlert(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      
      await createAlert(formData)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchAlerts()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '新增失败')
    console.error(error)
  }
}


const detectTypeLabel = (type) => {
  const map = { obstacle: '障碍物', defect: '缺陷', anomaly: '异常行为', other: '其他' }
  return map[type] || type
}
const detectTypeTag = (type) => {
  const map = { obstacle: 'danger', defect: 'warning', anomaly: 'info', other: '' }
  return map[type] || ''
}
const statusLabel = (status) => {
  const map = { pending: '待处理', processing: '处理中', resolved: '已解决', ignored: '已忽略' }
  return map[status] || status
}
const statusTag = (status) => {
  const map = { pending: 'danger', processing: 'warning', resolved: 'success', ignored: 'info' }
  return map[status] || ''
}


onMounted(() => {
  fetchAlerts()
})
</script>

<style scoped>
.alert-manage {
  padding: 20px;
}
.filter-card {
  margin-bottom: 20px;
}
.filter-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
.table-card {
  margin-top: 10px;
}
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>