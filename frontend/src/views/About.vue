<template>
  <section class="about">
    <el-card>
      <template #header>
        <div class="card-header">关于系统</div>
      </template>

      <h2>UAV 无人机巡检系统</h2>
      <p>当前框架版本：Vue 3 + Django</p>

      <el-divider />

      <h3>系统简介</h3>
      <p>
        这是一个面向无人机巡检业务的管理系统基础框架，支持设备管理、任务管理、
        运行状态统计和 RESTful API 扩展。
      </p>

      <h3>主要模块</h3>
      <el-tree :data="features" node-key="id" default-expand-all />

      <el-divider />

      <h3>技术栈</h3>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12">
          <h4>前端</h4>
          <ul>
            <li>Vue 3</li>
            <li>Vite</li>
            <li>Pinia</li>
            <li>Element Plus</li>
            <li>Axios</li>
          </ul>
        </el-col>
        <el-col :xs="24" :sm="12">
          <h4>后端</h4>
          <ul>
            <li>Django</li>
            <li>Django REST Framework</li>
            <li>django-cors-headers</li>
            <li>SQLite 默认开发库，可扩展 MySQL</li>
          </ul>
        </el-col>
      </el-row>
    </el-card>
  </section>
</template>

<script setup>
import { ref } from 'vue'

const features = ref([
  {
    id: 1,
    label: '任务管理',
    children: [
      { id: 11, label: '创建、编辑和删除巡检任务' },
      { id: 12, label: '按设备和状态查询任务' },
      { id: 13, label: '记录任务进度和计划时间' }
    ]
  },
  {
    id: 2,
    label: '设备管理',
    children: [
      { id: 21, label: '维护无人机设备档案' },
      { id: 22, label: '跟踪在线状态和电量' },
      { id: 23, label: '按设备编号查询详情' }
    ]
  },
  {
    id: 3,
    label: '统计概览',
    children: [
      { id: 31, label: '任务总数和完成数量' },
      { id: 32, label: '活跃任务数量' },
      { id: 33, label: '设备总数和在线设备数量' }
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
  font-weight: 700;
}

h2 {
  margin-top: 0;
  color: #303133;
}

h3 {
  margin-top: 1.5rem;
  color: #606266;
}

h4 {
  color: #606266;
}

p,
ul {
  line-height: 1.8;
}

ul {
  margin-left: 1.5rem;
}
</style>
