<template>
  <div class="about">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>关于系统</span>
        </div>
      </template>
      <h2>UAV 无人机巡检系统</h2>
      <p>版本：1.0.0</p>
      
      <el-divider />
      
      <h3>系统简介</h3>
      <p>
        这是一个现代化的无人机巡检管理系统，集成了先进的飞行控制、数据处理和可视化分析技术。
        系统支持多种巡检任务，包括电力设施巡检、建筑监测、农业管理等应用场景。
      </p>

      <h3>主要功能特性</h3>
      <el-tree :data="features" node-key="id" />

      <el-divider />

      <h3>技术栈</h3>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12">
          <h4>前端</h4>
          <ul>
            <li>Vue 3</li>
            <li>Vite</li>
            <li>Pinia (状态管理)</li>
            <li>Element Plus (UI 组件库)</li>
          </ul>
        </el-col>
        <el-col :xs="24" :sm="12">
          <h4>后端</h4>
          <ul>
            <li>Spring Boot</li>
            <li>JDK 1.8</li>
            <li>MySQL/PostgreSQL</li>
            <li>Redis (缓存)</li>
          </ul>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElCard, ElDivider, ElTree, ElRow, ElCol } from 'element-plus'

const features = ref([
  {
    id: 1,
    label: '任务管理',
    children: [
      { id: 11, label: '创建和编辑巡检任务' },
      { id: 12, label: '任务调度和分配' },
      { id: 13, label: '进度监控' }
    ]
  },
  {
    id: 2,
    label: '设备管理',
    children: [
      { id: 21, label: '设备注册和配置' },
      { id: 22, label: '实时状态监控' },
      { id: 23, label: '远程控制' }
    ]
  },
  {
    id: 3,
    label: '数据分析',
    children: [
      { id: 31, label: '巡检数据收集' },
      { id: 32, label: '图表统计分析' },
      { id: 33, label: '报告生成' }
    ]
  }
])
</script>

<style scoped>
.about {
  width: 100%;
}

.card-header {
  font-size: 1.1rem;
  font-weight: bold;
}

h2 {
  color: #303133;
  margin-top: 0;
}

h3 {
  color: #606266;
  margin-top: 1.5rem;
}

h4 {
  color: #909399;
}

ul {
  margin-left: 1.5rem;
  line-height: 1.8;
}
</style>
