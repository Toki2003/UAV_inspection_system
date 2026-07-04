<template>
  <div class="layout">

    <!-- 左侧菜单 -->
    <aside class="sidebar">
      <div class="logo">UAV 系统</div>

      <el-menu router :default-active="route.path">

        <el-menu-item
          v-for="item in menus"
          :key="item.path"
          :index="item.path"
        >
          {{ item.title }}
        </el-menu-item>

      </el-menu>
    </aside>

    <!-- 内容区 -->
    <main class="content">
      <router-view />
    </main>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { usePermissionStore } from '@/store/permission'

const route = useRoute()
const permissionStore = usePermissionStore()

// 菜单从 permissionStore 获取（唯一源头）
const menus = computed(() => permissionStore.menus)
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 220px;
  background: #001529;
  color: white;
}

.logo {
  height: 50px;
  line-height: 50px;
  text-align: center;
  background: #002140;
  font-weight: bold;
}

.content {
  flex: 1;
  padding: 16px;
  background: #f5f5f5;
}
</style>