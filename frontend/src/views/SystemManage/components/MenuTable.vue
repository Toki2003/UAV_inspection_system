<template>
  <div class="menu-table">
    <el-card>
      <template #header>
        <div>菜单管理（MOCK模式）</div>
      </template>

      <div style="margin-bottom: 10px;">
        <el-input
          v-model="search"
          placeholder="搜索菜单"
          clearable
          style="width: 240px"
        />
      </div>

      <el-table :data="filteredMenus" border>
        <el-table-column prop="title" label="菜单名称" />
        <el-table-column prop="path" label="路径" />
        <el-table-column prop="icon" label="图标" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { mockMenus } from '@/mock/system'

const search = ref('')

const filteredMenus = computed(() => {
  if (!search.value) return mockMenus
  return mockMenus.filter(i =>
    i.title?.includes(search.value)
  )
})
</script>

<style scoped>
.menu-table {
  padding: 10px;
}
</style>