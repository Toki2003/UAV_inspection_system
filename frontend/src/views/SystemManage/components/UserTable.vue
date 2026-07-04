<template>
  <div class="user-table">

    <!-- 搜索栏 -->
    <div class="toolbar">
      <el-input
        v-model="search"
        placeholder="搜索用户名 / 姓名"
        clearable
        style="width: 240px"
        @keyup.enter="loadUsers"
        @clear="loadUsers"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-button type="primary" @click="loadUsers">
        刷新
      </el-button>

      <el-button type="success" @click="handleAdd">
        添加用户（占位）
      </el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="list" v-loading="loading" border stripe>
      <el-table-column prop="username" label="账号" width="160" />
      <el-table-column prop="real_name" label="姓名" width="160" />

      <el-table-column label="角色" width="140">
        <template #default="{ row }">
          {{ row.role_name || '未分配' }}
        </template>
      </el-table-column>

      <el-table-column prop="phone" label="电话" width="160" />

      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="handleEdit(row)">
            编辑
          </el-button>

          <el-button size="small" type="danger" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>

    </el-table>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

// ✅ 直接用 Mock（先跑通最重要）
import { mockUsers } from '@/mock/system'

// ================= 数据 =================
const list = ref([])
const loading = ref(false)
const search = ref('')

// ================= 加载数据 =================
const loadUsers = async () => {
  loading.value = true

  try {
    let data = mockUsers

    // 搜索过滤
    if (search.value) {
      data = data.filter(i =>
        i.username.includes(search.value) ||
        i.real_name.includes(search.value)
      )
    }

    list.value = data
  } catch (err) {
    console.log(err)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// ================= 生命周期 =================
onMounted(() => {
  loadUsers()
})

// ================= 操作 =================
const handleAdd = () => {
  ElMessage.info('新增功能（后面再接后端）')
}

const handleEdit = (row) => {
  console.log('编辑：', row)
  ElMessage.info('编辑功能（后面做弹窗）')
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定删除用户 ${row.username} 吗？`,
    '提示',
    { type: 'warning' }
  ).then(() => {
    list.value = list.value.filter(i => i.id !== row.id)
    ElMessage.success('删除成功（Mock）')
  }).catch(() => {})
}
</script>

<style scoped>
.user-table {
  padding: 10px;
}

.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}
</style>