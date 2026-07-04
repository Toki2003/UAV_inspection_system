<template>
  <el-dialog v-model="visible" title="角色管理" width="460px">

    <el-form :model="form" label-width="80px">

      <el-form-item label="角色名">
        <el-input v-model="form.name" />
      </el-form-item>

      <el-form-item label="描述">
        <el-input v-model="form.desc" />
      </el-form-item>

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
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

// ================= 状态 =================
const visible = ref(false)
const saving = ref(false)

const form = reactive({
  id: null,
  name: '',
  desc: ''
})

// ================= 打开弹窗 =================
const open = (row = null) => {
  visible.value = true

  // 初始化表单
  form.id = row?.id || null
  form.name = row?.name || ''
  form.desc = row?.desc || ''
}

// ================= 提交 =================
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

    if (form.id) {
      await request.put(`/system/roles/${form.id}/`, payload)
      ElMessage.success('更新成功')
    } else {
      await request.post('/system/roles/', payload)
      ElMessage.success('创建成功')
    }

    visible.value = false
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
