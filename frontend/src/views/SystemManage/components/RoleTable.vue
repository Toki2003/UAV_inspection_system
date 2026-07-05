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
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-button type="primary" @click="loadRoles">查询</el-button>

      <!-- 新增角色：拥有 role:create 权限即可操作 -->
      <el-button v-permission="'role:create'" type="success" @click="openDialog()">新增角色</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="list" border stripe v-loading="loading">
      <el-table-column prop="name" label="角色名称" width="160" />
      <el-table-column prop="desc" label="描述" />

      <el-table-column label="操作" width="220">
        <template #default="{ row }">

          <!-- 编辑：拥有 role:update 权限即可操作 -->
          <el-button
            v-permission="'role:update'"
            type="primary"
            size="small"
            @click="openDialog(row)"
          >
            编辑
          </el-button>

          <!-- 删除：基础角色不可删除，拥有 role:delete 权限即可操作 -->
          <el-button
            v-if="!isBaseRole(row)"
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
/**
 * RoleTable - 角色列表管理组件
 *
 * 职责：展示角色列表、搜索过滤、创建 / 编辑 / 删除角色。
 * 权限控制：
 *   - 新增按钮受 role:create 权限控制（v-permission 指令）
 *   - 编辑按钮受 role:update 权限控制
 *   - 删除按钮受 role:delete 权限控制，且基础角色不可删除
 *   - 删除 / 编辑角色后从后端刷新当前用户权限，确保前后端一致
 */
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { useAppStore } from '@/store'

import RoleDialog from './RoleDialog.vue'

import {
  getRoleList,
  deleteRole
} from '@/api/system'

const store = useAppStore()
const list = ref([])
const loading = ref(false)
const search = ref('')
const dialogRef = ref(null)

/** 系统基础角色名称，这些角色不可删除 */
const BASE_ROLE_NAMES = ['super_admin', 'admin', 'user']

/** 判断角色是否为基础角色（不可删除） */
const isBaseRole = (row) => BASE_ROLE_NAMES.includes(row?.name)



/** 加载角色列表，支持前端本地搜索过滤 */
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

/**
 * 打开角色编辑弹窗
 * @param {Object|null} row - 编辑时传入角色数据，新建时传 null
 */
const openDialog = (row = null) => {
  dialogRef.value.open(
    row || {
      id: null,
      name: '',
      desc: ''
    }
  )
}

/** 删除角色，删除后从后端刷新当前用户权限 */
const handleDelete = async (row) => {
  await ElMessageBox.confirm(
    '确认删除该角色？',
    '提示',
    { type: 'warning' }
  )

  try {
    await deleteRole(row.id)
    ElMessage.success('删除成功')
    
    // 角色删除可能影响关联用户的权限状态，从后端刷新当前用户权限
    await store.refreshPermissionsFromBackend()
    
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
