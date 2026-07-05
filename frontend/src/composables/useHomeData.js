import { ref, onMounted } from 'vue'

const fallbackHome = {
  platformTitle: '城市轨道交通无人机智能巡检与缺陷管理平台',
  operator: { name: '管理员', role: '系统管理员' },
  updatedAt: '2026-07-05 09:30:00',
  menu: [
    { id: 'home', label: '首页', hint: '平台总览' },
    { id: 'console', label: '主控台', hint: '巡检调度入口' },
    { id: 'alerts', label: '告警管理', hint: '异常告警处置' },
    { id: 'statistics', label: '告警统计', hint: '告警趋势分析' },
    { id: 'ai', label: 'AI检测', hint: '缺陷识别结果' },
    { id: 'tasks', label: '巡检任务', hint: '任务进度查询' },
    { id: 'system', label: '系统管理', hint: '平台基础配置' },
  ],
  airports: [
    {
      name: '工业大学机场',
      status: '在线',
      temperature: '24.2°C',
      wind: '5.9 m/s',
      humidity: '35%',
      battery: '94%',
      position: '西南环线 2 号点',
    },
    {
      name: '马贝机场',
      status: '在线',
      temperature: '3.1°C',
      wind: '3.3 m/s',
      humidity: '11%',
      battery: '94%',
      position: '车辆段北侧',
    },
  ],
  alarms: [
    { type: '轨道检测', desc: 'AI检测发现疑似异物侵限', time: '2026-07-05 09:18' },
    { type: '设备巡检', desc: '机场电池仓温度轻微异常', time: '2026-07-05 08:46' },
    { type: '桥梁检测', desc: '桥墩表面疑似裂纹', time: '2026-07-04 17:30' },
    { type: '接触网', desc: '图像清晰度低，建议复检', time: '2026-07-04 16:08' },
  ],
  alarmStats: {
    total: 385,
    rail: '88%',
    contact: '2%',
    bridge: '0%',
    protection: '10%',
  },
  security: {
    safeDays: 82,
    todayWarnings: 0,
    recentAbnormal: 385,
    yearWarnings: 4445,
  },
  faultRates: [
    { name: '铁路', value: 0, count: '0/340' },
    { name: '接触网', value: 0, count: '0/6' },
    { name: '桥梁', value: 0, count: '0/0' },
  ],
  aiDetections: [
    { title: 'AI检测发现：异物侵限', time: '2026-07-05 09:18' },
    { title: '桥墩表面状态识别完成', time: '2026-07-05 08:55' },
  ],
  tasks: [
    { type: '轨道检测', status: '扫描中', time: '2026-07-05 09:20' },
    { type: '轨道检测', status: '扫描中', time: '2026-07-05 09:10' },
    { type: '桥梁巡检', status: '待检测', time: '2026-07-05 10:00' },
    { type: '轨道检测', status: '已完成', time: '2026-07-04 18:20' },
  ],
  flightStats: [
    { airport: '工业大学机场', tasks: '6次', distance: '11.00km', hours: '1.80小时' },
    { airport: '马贝机场', tasks: '0次', distance: '0.00km', hours: '0.00小时' },
  ],
}

export function useHomeData() {
  const homeData = ref({ ...fallbackHome })
  const loading = ref(true)
  const apiError = ref('')

  async function fetchHomeData() {
    loading.value = true
    apiError.value = ''
    try {
      const response = await fetch('/api/home')
      if (response.ok) {
        const data = await response.json()
        homeData.value = { ...fallbackHome, ...data }
      } else {
        throw new Error('not ok')
      }
    } catch {
      apiError.value = '后端接口暂不可用，当前显示本地演示数据'
      homeData.value = { ...fallbackHome }
    } finally {
      loading.value = false
    }
  }

  onMounted(() => {
    fetchHomeData()
  })

  return { homeData, loading, apiError }
}
