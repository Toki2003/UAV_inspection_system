<template>
  <div>
    <el-card>
      <template #header>角色管理</template>

      <el-table :data="roleList" border>
        <el-table-column prop="name" label="角色名称" />
        <el-table-column prop="desc" label="描述" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getRoleList } from '@/api/system'

const roleList = ref([])

const loadData = async () => {
  const res = await getRoleList()
  roleList.value = res.data
}

onMounted(() => {
  loadData()
})
</script>