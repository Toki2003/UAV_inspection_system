<template>
  <div class="role-table">

    <!-- 工具栏 -->
    <div class="toolbar">
      <el-input
        v-model="search"
        placeholder="搜索角色"
        clearable
        style="width: 220px"
        @keyup.enter="loadRoles"
        @clear="loadRoles"
      />

      <el-button type="primary" @click="loadRoles">刷新</el-button>

      <el-button v-permission="'role:create'" type="success" @click="openDialog()">新增角色</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="list" border stripe v-loading="loading">
      <el-table-column prop="name" label="角色名称" width="160" />
      <el-table-column prop="desc" label="描述" />

      <el-table-column label="操作" width="220">
        <template #default="{ row }">

          <!-- 编辑：需要 role:update 权限 -->
          <el-button
            v-permission="'role:update'"
            type="primary"
            size="small"
            @click="openDialog(row)"
          >
            编辑
          </el-button>

          <!-- 删除：需要 role:delete 权限 -->
          <el-button
            v-permission="'role:delete'"
            type="danger"
            size="small"
            @click="handleDelete(row)"
          >
            删除
          </el-button>

        </template>
      </el-table-column>
    </el-table>

    <!-- 角色权限弹窗 -->
    <RoleDialog
      ref="dialogRef"
      @success="loadRoles"
    />

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import RoleDialog from './RoleDialog.vue'

import {
  getRoleList,
  deleteRole
} from '@/api/system'

// ================= 数据 =================
const list = ref([])
const loading = ref(false)
const search = ref('')

// 弹窗引用
const dialogRef = ref(null)

// ================= 加载角色 =================
const loadRoles = async () => {
  loading.value = true
  try {
    const res = await getRoleList()
    let data
    if (Array.isArray(res)) {
      data = res
    } else if (res?.data?.results) {
      data = res.data.results
    } else if (Array.isArray(res?.data)) {
      data = res.data
    } else {
      data = []
    }

    if (search.value) {
      data = data.filter(i =>
        (i.name || '').includes(search.value) ||
        (i.desc || '').includes(search.value)
      )
    }

    list.value = data
  } finally {
    loading.value = false
  }
}

onMounted(loadRoles)

// ================= 打开弹窗（统一入口） =================
const openDialog = (row = null) => {
  dialogRef.value.open(
    row || {
      id: null,
      name: '',
      desc: ''
    }
  )
}

// ================= 删除 =================
const handleDelete = async (row) => {
  await ElMessageBox.confirm(
    '确认删除该角色？',
    '提示',
    { type: 'warning' }
  )

  try {
    await deleteRole(row.id)
    ElMessage.success('删除成功')
    
    // 注意：角色删除后，不需要刷新当前用户的权限
    // 因为角色删除不影响其他用户的权限
    // 只有当用户自己的角色被删除时，才需要重新登录
    
    loadRoles()
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '删除失败')
  }
}
</script>

<style scoped>
.role-table {
  padding: 10px;
}

.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}
</style>
