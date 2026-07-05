<template>
  <el-dialog v-model="visible" title="角色管理" width="600px">

    <el-form :model="form" label-width="80px">

      <el-form-item label="角色名">
        <el-input v-model="form.name" :disabled="isBaseRole" />
      </el-form-item>

      <el-form-item label="描述">
        <el-input v-model="form.desc" type="textarea" :rows="2" :disabled="isBaseRole" />
      </el-form-item>

      <!-- 权限配置：分字段控制 -->
      <el-form-item label="权限配置" v-if="!isBaseRole">
        <!-- 管理员：可编辑权限树 -->
        <el-tree
          v-if="canEditPermissions"
          ref="treeRef"
          :data="permissionTree"
          show-checkbox
          node-key="id"
          :props="{ label: 'label', children: 'children' }"
          :default-checked-keys="form.permissions"
          :check-strictly="false"
          @check="handleCheckChange"
          style="max-height: 300px; overflow-y: auto; border: 1px solid #dcdfe6; padding: 10px;"
        />
        <!-- 非管理员：只读提示 -->
        <div v-else class="permission-readonly">
          仅管理员可修改
        </div>
      </el-form-item>

      <el-alert
        v-else
        :title="baseRoleAlertTitle"
        type="info"
        :closable="false"
        show-icon
      />

    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submit" :loading="saving" :disabled="isBaseRole">
        保存
      </el-button>
    </template>

  </el-dialog>
</template>

<script setup>
/**
 * RoleDialog - 角色编辑弹窗组件
 *
 * 职责：创建 / 编辑角色，包括名称、描述和权限树配置。
 * 设计决策：
 *   - 基础角色（super_admin / admin / user）的所有字段均不可编辑，弹窗仅展示提示信息
 *   - 权限树仅管理员（super_admin / admin）可编辑，非管理员展示只读提示
 *   - 提交后调用 store.refreshPermissionsFromBackend() 从后端刷新权限，确保前后端一致
 */
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'
import { getPermissionTree } from '@/api/system'
import { useAppStore } from '@/store'

const store = useAppStore()
const visible = ref(false)
const saving = ref(false)
const permissionTree = ref([])
const treeRef = ref(null)

/** 当前编辑的角色是否为基础角色（名称、描述、权限均不可修改） */
const isBaseRole = ref(false)

/** 当前用户是否为管理员（仅管理员可修改角色权限配置） */
const canEditPermissions = computed(() => {
  const roleName = store.user?.role?.name
  return roleName === 'super_admin' || roleName === 'admin'
})



/** 系统基础角色名称，与后端 BASE_ROLE_NAMES 保持一致 */
const BASE_ROLE_NAMES = ['super_admin', 'admin', 'user']

/** 基础角色提示信息，编辑时展示只读说明 */
const BASE_ROLE_ALERTS = {
  super_admin: '超级管理员拥有所有系统权限，名称、描述和权限均不可修改',
  admin: '管理员为基础角色，名称、描述和权限均不可修改',
  user: '普通用户为基础角色，名称、描述和权限均不可修改'
}

/** 根据当前角色名返回对应的只读提示信息 */
const baseRoleAlertTitle = computed(() => {
  return BASE_ROLE_ALERTS[form.name] || '基础角色的信息不可修改'
})

const form = reactive({
  id: null,
  name: '',
  desc: '',
  permissions: []
})

/** 组件挂载时从后端加载权限树结构 */
onMounted(async () => {
  try {
    const res = await getPermissionTree()
    permissionTree.value = res.data || []
  } catch (err) {
    console.error('加载权限树失败:', err)
  }
})

/**
 * 打开弹窗（由父组件通过 ref 调用）
 * @param {Object|null} row - 编辑时传入角色数据，新建时传 null
 */
const open = (row = null) => {
  visible.value = true

  form.id = row?.id || null
  form.name = row?.name || ''
  form.desc = row?.desc || ''
  form.permissions = row?.permissions || []

  isBaseRole.value = BASE_ROLE_NAMES.includes(row?.name)

  // 延迟设置树的选中状态，等待 el-tree 渲染完成后再勾选
  setTimeout(() => {
    if (treeRef.value && form.permissions.length > 0 && !isBaseRole.value) {
      treeRef.value.setCheckedKeys(form.permissions, false)
    }
  }, 100)
}

// ================= 权限树勾选 =================
/**
 * 权限树勾选回调
 * check-strictly=false 时 Element Plus 自动处理父子联动，无需额外逻辑
 */
const handleCheckChange = () => {}

/**
 * 提交角色创建 / 更新请求
 * 仅管理员提交 permissions 字段，非管理员不发送该字段
 * 提交成功后从后端刷新权限，确保角色权限变更立即同步到当前会话
 */
const submit = async () => {
  if (!form.name.trim()) {
    ElMessage.warning('请输入角色名')
    return
  }

  saving.value = true
  try {
    const payload = {
      name: form.name,
      desc: form.desc
    }

    if (canEditPermissions.value) {
      const checkedKeys = treeRef.value ? treeRef.value.getCheckedKeys(false) : []
      payload.permissions = checkedKeys
    }

    if (form.id) {
      await request.put(`/system/roles/${form.id}/`, payload)
      ElMessage.success('更新成功')
    } else {
      await request.post('/system/roles/', payload)
      ElMessage.success('创建成功')
    }

    visible.value = false

    // 角色权限变更后，从后端刷新当前用户权限（后端为权威来源）
    await store.refreshPermissionsFromBackend()
    
    emit('success')
  } catch (err) {
    // DRF 验证错误格式: {"name": ["role with this name already exists."]}
    const drfErrors = err.response?.data
    if (drfErrors && typeof drfErrors === 'object' && !drfErrors.message) {
      const msgs = Object.values(drfErrors).flat().join('; ')
      ElMessage.error(msgs || '操作失败')
    } else {
      ElMessage.error(drfErrors?.message || err.message || '操作失败')
    }
  } finally {
    saving.value = false
  }
}

const emit = defineEmits(['success'])

/** 暴露 open 方法供父组件调用 */
defineExpose({ open })
</script>

<style scoped>
.permission-readonly {
  padding: 12px;
  color: #999;
  background: #f5f5f5;
  border-radius: 6px;
}
</style>
