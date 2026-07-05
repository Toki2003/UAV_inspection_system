<script setup>
import { ref } from 'vue'
import TopBar from '@/components/TopBar.vue'

const menuVisible = ref(true)

function toggleMenu() {
  menuVisible.value = !menuVisible.value
}
</script>

<template>
  <main class="dashboard-shell" :class="{ 'menu-collapsed': !menuVisible }">
    <TopBar
      :menu-visible="menuVisible"
      @toggle-menu="toggleMenu"
    />
    <div class="layout-content">
      <router-view />
    </div>
  </main>
</template>

<style scoped>
.dashboard-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-content {
  flex: 1;
  min-height: 0;
}
</style>
