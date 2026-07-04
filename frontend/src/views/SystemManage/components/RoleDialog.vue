<template>
  <el-dialog v-model="visible" title="角色管理" width="600px">

    <el-form :model="form" label-width="80px">

      <el-form-item label="角色名">
        <el-input v-model="form.name" />
      </el-form-item>

      <el-form-item label="描述">
        <el-input v-model="form.desc" type="textarea" :rows="2" />
      </el-form-item>

      <el-form-item label="权限配置" v-if="!isAdminRole">
        <el-tree
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
      </el-form-item>

      <el-alert
        v-else
        title="超级管理员拥有所有系统权限，不可修改"
        type="info"
        :closable="false"
        show-icon
      />

    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submit" :loading="saving">
        保存
      </el-button>
    </template>

  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'
import { getPermissionTree } from '@/api/system'

// ================= 状态 =================
const visible = ref(false)
const saving = ref(false)
const permissionTree = ref([])
const treeRef = ref(null)
const isAdminRole = ref(false) // 是否为 admin 角色

const form = reactive({
  id: null,
  name: '',
  desc: '',
  permissions: []
})

// ================= 加载权限树 =================
onMounted(async () => {
  try {
    const res = await getPermissionTree()
    permissionTree.value = res.data || []
  } catch (err) {
    console.error('加载权限树失败:', err)
  }
})

// ================= 打开弹窗 =================
const open = (row = null) => {
  visible.value = true

  // 初始化表单
  form.id = row?.id || null
  form.name = row?.name || ''
  form.desc = row?.desc || ''
  form.permissions = row?.permissions || []
  
  // 判断是否为 admin 角色
  isAdminRole.value = row?.name === 'admin'

  // 延迟设置树的选中状态，确保树已渲染
  setTimeout(() => {
    if (treeRef.value && form.permissions.length > 0 && !isAdminRole.value) {
      treeRef.value.setCheckedKeys(form.permissions, false)
    }
  }, 100)
}

// ================= 权限树勾选变化 =================
const handleCheckChange = (data, checked) => {
  // check-strictly=false 时，Element Plus 会自动处理父子联动
  // 勾选父节点会自动勾选所有子节点
  // 取消父节点会自动取消所有子节点
  // 无需额外处理
}

// ================= 提交 =================
const submit = async () => {
  if (!form.name.trim()) {
    ElMessage.warning('请输入角色名')
    return
  }

  // 从树获取选中的权限（只获取叶子节点的权限码）
  const checkedKeys = treeRef.value ? treeRef.value.getCheckedKeys(false) : []
  // getCheckedKeys(false) - 只获取被选中的叶子节点，不包含父节点
  // 这样后端只需要存储叶子节点权限，登录时根据叶子节点推导父模块权限

  saving.value = true
  try {
    const payload = {
      name: form.name,
      desc: form.desc,
      permissions: checkedKeys
    }

    if (form.id) {
      await request.put(`/system/roles/${form.id}/`, payload)
      ElMessage.success('更新成功')
    } else {
      await request.post('/system/roles/', payload)
      ElMessage.success('创建成功')
    }

    visible.value = false
    
    // 注意：角色权限修改后，不需要刷新当前用户的权限
    // 因为角色权限变更不影响当前操作者的权限
    // 只有当用户自己的角色被修改时，才需要重新登录或刷新权限
    
    // 通知父组件刷新
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

// 暴露给父组件
defineExpose({ open })
</script>
