<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Activity,
  BatteryCharging,
  CalendarClock,
  ChevronRight,
  Droplets,
  Eye,
  Gauge,
  Home,
  Plane,
  Play,
  Radio,
  ShieldCheck,
  Thermometer,
  Wind,
} from 'lucide-vue-next'
import { useHomeData } from '@/composables/useHomeData.js'
import mapBase from '@/assets/map-base.png'

const router = useRouter()
const { homeData, loading, apiError } = useHomeData()

const currentMenu = computed(() => {
  return homeData.value.menu.find((item) => item.id === 'home') || homeData.value.menu[0]
})

const currentIcon = computed(() => Home)

const mapStyle = computed(() => ({
  backgroundImage: `linear-gradient(180deg, rgba(6, 22, 35, 0.12), rgba(5, 15, 24, 0.42)), url(${mapBase})`,
}))

const mapMarkers = [
  { id: 'station-a', label: '工业大学机场', left: '31%', top: '55%' },
  { id: 'station-b', label: '马贝机场', left: '76%', top: '24%' },
  { id: 'uav', label: '巡检无人机', left: '52%', top: '45%' },
]
</script>

<template>
  <div>
    <!-- Loading / Error notice -->
    <div v-if="loading || apiError" class="system-notice" :class="{ warning: apiError }">
      <Activity :size="16" />
      <span>{{ loading ? '正在加载首页数据' : apiError }}</span>
    </div>

    <!-- Main dashboard grid -->
    <section class="dashboard-grid" aria-label="平台首页">
      <!-- 左侧面板 -->
      <aside class="side-stack">
        <section class="panel airport-panel">
          <div class="panel-header">
            <h2>机场信息</h2>
            <button type="button">详情 <ChevronRight :size="14" /></button>
          </div>
          <div class="airport-list">
            <article v-for="airport in homeData.airports" :key="airport.name" class="airport-item">
              <div class="airport-title">
                <span class="status-dot"></span>
                <strong>{{ airport.name }}</strong>
                <small>{{ airport.position }}</small>
              </div>
              <div class="airport-metrics">
                <span><Thermometer :size="14" />{{ airport.temperature }}</span>
                <span><Wind :size="14" />{{ airport.wind }}</span>
                <span><Droplets :size="14" />{{ airport.humidity }}</span>
                <span><BatteryCharging :size="14" />{{ airport.battery }}</span>
              </div>
            </article>
          </div>
        </section>

        <section class="panel">
          <div class="panel-header">
            <h2>告警管理</h2>
            <button type="button">详情 <ChevronRight :size="14" /></button>
          </div>
          <div class="table-head">
            <span>类型</span>
            <span>描述</span>
            <span>时间</span>
          </div>
          <div class="compact-table">
            <div v-for="alarm in homeData.alarms" :key="`${alarm.type}-${alarm.time}`" class="table-row">
              <span>{{ alarm.type }}</span>
              <span>{{ alarm.desc }}</span>
              <span>{{ alarm.time }}</span>
            </div>
          </div>
        </section>

        <section class="panel stat-panel">
          <div class="panel-header">
            <h2>告警统计</h2>
            <button type="button">详情 <ChevronRight :size="14" /></button>
          </div>
          <div class="stat-content">
            <div class="ring-meter">
              <span>{{ homeData.alarmStats.total }}</span>
              <small>报警总数</small>
            </div>
            <div class="legend-grid">
              <span><i class="legend cyan"></i>铁路 {{ homeData.alarmStats.rail }}</span>
              <span><i class="legend red"></i>接触网 {{ homeData.alarmStats.contact }}</span>
              <span><i class="legend violet"></i>桥梁 {{ homeData.alarmStats.bridge }}</span>
              <span><i class="legend green"></i>保护区 {{ homeData.alarmStats.protection }}</span>
            </div>
          </div>
        </section>
      </aside>

      <!-- 中间地图 -->
      <section class="map-panel">
        <div class="map-toolbar">
          <div class="module-chip">
            <component :is="currentIcon" :size="17" />
            <span>{{ currentMenu.label }}</span>
            <small>{{ currentMenu.hint }}</small>
          </div>
          <div class="time-chip">
            <CalendarClock :size="15" />
            <span>{{ homeData.updatedAt }}</span>
          </div>
        </div>

        <div class="map-scene" :style="mapStyle">
          <svg class="route-layer" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
            <polyline points="12,72 31,55 52,45 76,24 92,18" />
          </svg>

          <button
            v-for="marker in mapMarkers"
            :key="marker.id"
            class="map-marker"
            :class="marker.id"
            type="button"
            :style="{ left: marker.left, top: marker.top }"
          >
            <Radio v-if="marker.id !== 'uav'" :size="16" />
            <Plane v-else :size="16" />
            <span>{{ marker.label }}</span>
          </button>

          <button class="start-button" type="button" @click="router.push('/dashboard')">
            <Play :size="17" />
            <strong>启动检测</strong>
            <span>进入智能主控台</span>
          </button>
        </div>
      </section>

      <!-- 右侧面板 -->
      <aside class="side-stack">
        <section class="panel ai-panel">
          <div class="panel-header">
            <h2>AI检测</h2>
            <button type="button">详情 <ChevronRight :size="14" /></button>
          </div>
          <div class="ai-preview" aria-label="AI检测预览">
            <span class="scan-line"></span>
            <span class="detection-box one"></span>
            <span class="detection-box two"></span>
          </div>
          <div class="event-list">
            <div v-for="event in homeData.aiDetections" :key="event.time">
              <Eye :size="14" />
              <span>{{ event.title }}</span>
              <small>{{ event.time }}</small>
            </div>
          </div>
        </section>

        <section class="panel">
          <div class="panel-header">
            <h2>巡检任务</h2>
            <button type="button">详情 <ChevronRight :size="14" /></button>
          </div>
          <div class="table-head task-head">
            <span>巡检类型</span>
            <span>巡检状态</span>
            <span>巡检时间</span>
          </div>
          <div class="compact-table">
            <div v-for="task in homeData.tasks" :key="`${task.type}-${task.time}`" class="table-row">
              <span>{{ task.type }}</span>
              <span class="status-pill" :class="{ done: task.status === '已完成' }">{{ task.status }}</span>
              <span>{{ task.time }}</span>
            </div>
          </div>
        </section>
      </aside>
    </section>

    <!-- 底部统计 -->
    <section class="bottom-grid" aria-label="首页统计">
      <section class="panel security-panel">
        <div class="panel-header">
          <h2>系统安全</h2>
          <button type="button">本年度</button>
        </div>
        <div class="security-main">
          <ShieldCheck :size="30" />
          <div>
            <strong>{{ homeData.security.safeDays }}<small>天</small></strong>
            <span>安全运行天数</span>
          </div>
        </div>
        <div class="security-tags">
          <span>今日告警 {{ homeData.security.todayWarnings }}</span>
          <span>近30天异常 {{ homeData.security.recentAbnormal }}</span>
          <span>本年告警 {{ homeData.security.yearWarnings }}</span>
        </div>
      </section>

      <section class="panel fault-panel">
        <div class="panel-header">
          <h2>巡检故障处置率</h2>
          <button type="button">近1个月</button>
        </div>
        <div v-for="rate in homeData.faultRates" :key="rate.name" class="progress-row">
          <span>{{ rate.name }}</span>
          <div class="progress-track">
            <i :style="{ width: `${rate.value}%` }"></i>
          </div>
          <strong>{{ rate.value }}%</strong>
          <small>{{ rate.count }}</small>
        </div>
      </section>

      <section class="panel flight-panel">
        <div class="panel-header">
          <h2>飞行统计</h2>
          <button type="button">近1个月</button>
        </div>
        <div class="flight-head">
          <span>机场</span>
          <span>任务</span>
          <span>里程</span>
          <span>时长</span>
        </div>
        <div v-for="item in homeData.flightStats" :key="item.airport" class="flight-row">
          <span><Gauge :size="14" />{{ item.airport }}</span>
          <span>{{ item.tasks }}</span>
          <span>{{ item.distance }}</span>
          <span>{{ item.hours }}</span>
        </div>
      </section>
    </section>
  </div>
</template>
