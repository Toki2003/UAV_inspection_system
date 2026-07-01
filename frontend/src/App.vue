<template>
  <div class="app-container">
    <header class="app-header">
      <h1>UAV 无人机巡检系统</h1>
      <nav class="nav">
        <router-link to="/">首页</router-link>
        <router-link to="/dashboard">仪表板</router-link>
        <router-link to="/about">关于</router-link>
      </nav>
    </header>
    <main class="app-main">
      <router-view />
    </main>
    <footer class="app-footer">
      <p>&copy; 2024 UAV 巡检系统 - 版权所有</p>
    </footer>
  </div>
</template>

<script setup>
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
}

.app-header {
  background-color: #303133;
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  margin: 0 0 1rem 0;
  font-size: 1.5rem;
}

.nav {
  display: flex;
  gap: 2rem;
}

.nav a {
  color: white;
  text-decoration: none;
  transition: color 0.3s;
}

.nav a:hover {
  color: #409eff;
}

.app-main {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.app-footer {
  background-color: #f5f7fa;
  color: #606266;
  text-align: center;
  padding: 1rem;
  border-top: 1px solid #ebeef5;
}

.app-footer p {
  margin: 0;
}
</style>
