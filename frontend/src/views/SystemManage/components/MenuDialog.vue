<template>
  <el-dialog
    v-model="visible"
    :title="form.id ? '编辑菜单' : '新增菜单'"
    width="500px"
  >
    <el-form :model="form" label-width="100px">
      <el-form-item label="菜单名称">
        <el-input v-model="form.title" />
      </el-form-item>

      <el-form-item label="路径">
        <el-input v-model="form.path" />
      </el-form-item>

      <el-form-item label="图标">
        <el-input v-model="form.icon" />
      </el-form-item>

      <el-form-item label="排序">
        <el-input-number v-model="form.sort" :min="0" />
      </el-form-item>

      <el-form-item label="是否显示">
        <el-switch v-model="form.is_show" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive, ref } from 'vue'

const visible = ref(false)

const form = reactive({
  id: null,
  title: '',
  path: '',
  icon: '',
  sort: 0,
  is_show: true
})

const open = (data = null) => {
  if (data) {
    Object.assign(form, data)
  } else {
    Object.assign(form, {
      id: null,
      title: '',
      path: '',
      icon: '',
      sort: 0,
      is_show: true
    })
  }
  visible.value = true
}

const emit = defineEmits(['submit'])

const handleSubmit = () => {
  emit('submit', { ...form })
  visible.value = false
}

// 让父组件可以调用
defineExpose({ open })
</script>