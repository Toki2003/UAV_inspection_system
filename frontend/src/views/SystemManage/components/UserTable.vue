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

      <el-button v-permission="'user:create'" type="success" @click="handleAdd">
        添加用户
      </el-button>
    </div>

    <el-table :data="list" v-loading="loading" border stripe>

      <el-table-column prop="username" label="账号" width="160" />
      <el-table-column prop="real_name" label="姓名" width="160" />

      <el-table-column v-if="canAssignRole" label="角色" width="140">
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
            v-if="canOperateUser(row)"
            v-permission="'user:update'"
            size="small"
            type="primary"
            @click="handleEdit(row)"
          >
            编辑
          </el-button>

          <el-button
            v-if="canOperateUser(row) && row.id !== currentUserId"
            v-permission="'user:delete'"
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

        <el-form-item v-if="canAssignRole && !isSelfEdit" label="角色">
          <el-select v-model="form.role_id" placeholder="请选择角色" clearable style="width: 100%">
            <el-option
              v-for="r in availableRoles"
              :key="r.id"
              :label="r.name"
              :value="r.id"
            />
          </el-select>
        </el-form-item>

        <el-alert
          v-else-if="isSelfEdit && canAssignRole"
          title="不能修改自己的角色信息"
          type="info"
          :closable="false"
          show-icon
        />

        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>

        <el-form-item label="状态" v-if="!isSelfEdit">
          <el-switch v-model="form.is_active" />
        </el-form-item>

        <el-alert
          v-else
          title="不能修改自己的激活状态"
          type="warning"
          :closable="false"
          show-icon
        />

      </el-form>

      <template #footer>
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="loading">
          保存
        </el-button>
      </template>

    </el-dialog>

  </div>
</template>

<script setup>
/**
 * UserTable - 用户列表管理组件
 *
 * 职责：用户 CRUD、角色分配、状态管理。
 * 权限控制：
 *   - 添加按钮受 user:create 权限控制
 *   - 编辑 / 删除按钮受 user:update / user:delete 权限控制
 *   - 角色分配（canAssignRole）仅限 super_admin / admin
 *   - 层级保护：高权限可操作低权限用户，不能操作同级或更高
 *   - 自我保护：编辑自己时隐藏角色 / 状态修改控件
 *   - super_admin 角色唯一：已有用户拥有时从可选角色列表中过滤
 */
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

/** 是否正在编辑当前登录用户（控制自我保护 UI） */
const isSelfEdit = ref(false)

/**
 * 当前用户是否拥有角色分配权限
 * “分配用户角色”是独立的高权限操作，仅通过角色名称判断，不受自定义权限码影响
 */
const canAssignRole = computed(() => {
  const roleName = store.user?.role?.name
  return roleName === 'super_admin' || roleName === 'admin'
})

/** 超级管理员角色名称 */
const SUPER_ADMIN_ROLE = 'super_admin'

/** 角色层级：数值越大权限越高，高权限可操作低权限，不能操作同级或更高 */
const ROLE_LEVEL = {
  user: 1,
  admin: 2,
  super_admin: 3,
}

/**
 * 可用角色列表：如果已有用户拥有 super_admin 角色，则从可选列表中过滤掉
 * 设计意图：super_admin 角色唯一，不能分配给第二个用户
 */
const availableRoles = computed(() => {
  const hasSuperAdmin = list.value.some(u => u.role_name === SUPER_ADMIN_ROLE)
  if (hasSuperAdmin) {
    return roleList.value.filter(r => r.name !== SUPER_ADMIN_ROLE)
  }
  return roleList.value
})

/** 当前登录用户的角色等级 */
const currentUserLevel = computed(() => {
  const roleName = store.user?.role?.name
  return ROLE_LEVEL[roleName] || 0
})

/**
 * 判断当前用户是否可以操作目标用户（编辑 / 删除）
 * 层级保护：不能操作同级或更高权限的用户，编辑自己始终允许
 * 自定义角色（不在 ROLE_LEVEL 中）视为管理层（1.5），可操作普通用户但无法操作 admin / super_admin
 */
const canOperateUser = (row) => {
  if (row.id === currentUserId.value) return true
  const targetLevel = ROLE_LEVEL[row.role_name] || 0
  // 自定义角色默认视为管理层 1.5
  const myLevel = ROLE_LEVEL[store.user?.role?.name] ?? 1.5
  return myLevel > targetLevel
}

const form = reactive({
  id: null,
  username: '',
  real_name: '',
  password: '',
  role_id: null,
  phone: '',
  is_active: true
})

/** 加载角色列表，用于弹窗中的角色选择下拉框 */
const loadRoles = async () => {
  try {
    const res = await getRoleList()
    roleList.value = Array.isArray(res) ? res : (res?.data?.results || res?.data || [])
  } catch (e) {
    roleList.value = []
  }
}

/** 当前登录用户 ID，用于禁止自删和自我保护判断 */
const currentUserId = computed(() => store.user?.id)

/** 加载用户列表，支持后端搜索参数 */
const loadUsers = async () => {
  loading.value = true
  try {
    const res = await getUserList({ search: search.value })
    // 后端无分页时 data 为纯数组，有分页时为 { results: [...] }
    const rawData = res?.data
    if (Array.isArray(rawData)) {
      list.value = rawData
    } else if (rawData?.results && Array.isArray(rawData.results)) {
      list.value = rawData.results
    } else {
      console.warn('[UserTable] loadUsers: 意外的响应格式', res)
      list.value = []
    }
  } catch (err) {
    console.error('[UserTable] loadUsers failed:', err)
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadUsers()
  loadRoles()
})

/** 打开新增用户弹窗，完全重置表单状态 */
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
  
  isSelfEdit.value = false
  
  loadRoles()
  editVisible.value = true
}

/** 打开编辑用户弹窗，填充行数据 */
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
  
  isSelfEdit.value = row.id === currentUserId.value
  
  loadRoles()
  editVisible.value = true
}

/**
 * 保存用户（创建 / 更新）
 * 前端自我保护：编辑自己时不发送 role_id / is_active，无分配权限时不发送 role_id
 */
const handleSave = async () => {
  loading.value = true
  let saveSuccess = false
  try {
    const payload = { ...form }
    
    if (isSelfEdit.value) {
      delete payload.role_id
      delete payload.is_active
    }
    
    if (!canAssignRole.value) {
      delete payload.role_id
    }
    
    if (payload.id && !payload.password) {
      delete payload.password
    }
    delete payload.id

    if (form.id) {
      const res = await updateUser(form.id, payload)
      if (res?.code && res.code !== 200) {
        ElMessage.error(res.message || '更新失败')
      } else {
        ElMessage.success('更新成功')
        saveSuccess = true
      }
    } else {
      const res = await createUser(payload)
      if (res?.code && res.code !== 200) {
        ElMessage.error(res.message || '新增失败')
      } else {
        ElMessage.success('新增成功')
        saveSuccess = true
      }
    }

    editVisible.value = false
    isSelfEdit.value = false
    
    Object.assign(form, {
      id: null,
      username: '',
      real_name: '',
      password: '',
      role_id: null,
      phone: '',
      is_active: true
    })
  } catch (err) {
    ElMessage.error(err.response?.data?.message || err.message || '操作失败')
  } finally {
    loading.value = false
  }

  if (saveSuccess) {
    await loadUsers()
  }
}

/** 删除用户，前端二次校验不能删除自己 */
const handleDelete = async (row) => {
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

/** 关闭弹窗并重置所有状态 */
const handleCancel = () => {
  editVisible.value = false
  isSelfEdit.value = false
  
  Object.assign(form, {
    id: null,
    username: '',
    real_name: '',
    password: '',
    role_id: null,
    phone: '',
    is_active: true
  })
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