<template>
  <div class="user-table">

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

      <el-button v-permission="'system:user:add'" type="success" @click="handleAdd">
        添加用户
      </el-button>
    </div>

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

      <el-table-column label="操作" width="200">

        <template #default="{ row }">

          <el-button
            v-permission="'system:user:edit'"
            size="small"
            type="primary"
            @click="handleEdit(row)"
          >
            编辑
          </el-button>

          <el-button
            v-permission="'system:user:delete'"
            v-if="row.id !== currentUserId"
            size="small"
            type="danger"
            @click="handleDelete(row)"
          >
            删除
          </el-button>

        </template>

      </el-table-column>

    </el-table>

    <!-- 弹窗 -->
    <el-dialog v-model="editVisible" :title="form.id ? '用户编辑' : '新增用户'" width="500px">

      <el-form :model="form" label-width="80px">

        <el-form-item label="账号">
          <el-input v-model="form.username" />
        </el-form-item>

        <el-form-item label="姓名">
          <el-input v-model="form.real_name" />
        </el-form-item>

        <el-form-item v-if="!form.id" label="密码">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>

        <el-form-item label="角色">
          <el-select v-model="form.role_id" placeholder="请选择角色" clearable style="width: 100%">
            <el-option
              v-for="r in roleList"
              :key="r.id"
              :label="r.name"
              :value="r.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>

        <el-form-item label="状态">
          <el-switch v-model="form.is_active" />
        </el-form-item>

      </el-form>

      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="loading">
          保存
        </el-button>
      </template>

    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { useAppStore } from '@/store'

import {
  getUserList,
  updateUser,
  deleteUser,
  createUser,
  getRoleList
} from '@/api/system'

const store = useAppStore()
const list = ref([])
const loading = ref(false)
const search = ref('')

const editVisible = ref(false)
const roleList = ref([])

const form = reactive({
  id: null,
  username: '',
  real_name: '',
  password: '',
  role_id: null,
  phone: '',
  is_active: true
})

// 加载角色列表
const loadRoles = async () => {
  try {
    const res = await getRoleList()
    roleList.value = Array.isArray(res) ? res : (res?.data?.results || res?.data || [])
  } catch (e) {
    roleList.value = []
  }
}

// 当前登录用户 ID（用于禁止自删）
const currentUserId = computed(() => store.user?.id)

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await getUserList({ search: search.value })
    // 后端 DRF 分页格式: { count, results }
    list.value = res.data?.results || res.data || []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadUsers()
  loadRoles()
})

const handleAdd = () => {
  Object.assign(form, {
    id: null,
    username: '',
    real_name: '',
    password: '',
    role_id: null,
    phone: '',
    is_active: true
  })
  loadRoles() // 打开弹窗时刷新角色列表，确保新增的角色能同步显示
  editVisible.value = true
}

const handleEdit = (row) => {
  Object.assign(form, {
    id: row.id,
    username: row.username,
    real_name: row.real_name,
    password: '',
    role_id: row.role_id || row.role?.id || null,
    phone: row.phone,
    is_active: row.is_active
  })
  loadRoles() // 打开弹窗时刷新角色列表
  editVisible.value = true
}

const handleSave = async () => {
  loading.value = true
  try {
    const payload = { ...form }
    // 编辑时不发送空密码
    if (payload.id && !payload.password) {
      delete payload.password
    }
    // 不发送 id 字段
    delete payload.id

    if (form.id) {
      await updateUser(form.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createUser(payload)
      ElMessage.success('新增成功')
    }

    editVisible.value = false
    await loadUsers()
  } catch (err) {
    ElMessage.error(err.response?.data?.message || err.message || '操作失败')
  } finally {
    loading.value = false
  }
}

const handleDelete = async (row) => {
  // 前端二次校验：不能删除自己
  if (row.id === currentUserId.value) {
    ElMessage.warning('不能删除当前登录用户')
    return
  }

  await ElMessageBox.confirm('确定删除该用户吗？', '提示', {
    type: 'warning'
  })

  try {
    const res = await deleteUser(row.id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      await loadUsers()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '删除失败')
  }
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