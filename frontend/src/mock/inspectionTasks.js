export const mockInspectionTasks = [
  {
    id: 1001,
    name: '轨道交通 1 号线高架区间巡检',
    code: 'TASK-20260702-001',
    routeName: '1 号线 K12+300-K16+800',
    areaName: '高架桥梁与接触网区域',
    deviceName: 'DJI-Matrice-RTK-01',
    pilot: '张工',
    status: 'running',
    progress: 68,
    cleanStatus: '待清理',
    priority: '高',
    createdTime: '2026-07-02 09:20:00',
    startTime: '2026-07-02 09:45:00',
    endTime: '',
    rtspUrl: 'rtsp://127.0.0.1:8554/uav-line-1',
    description: '对高架区间轨道、桥梁外观、接触网支架和周边异物进行无人机巡检。',
    resultSummary: { photos: 126, videos: 4, defects: 3, warnings: 2 },
    steps: [
      { title: '任务创建', status: 'success', time: '09:20' },
      { title: '任务下发', status: 'success', time: '09:31' },
      { title: '无人机起飞', status: 'success', time: '09:45' },
      { title: '巡检执行', status: 'process', time: '10:18' },
      { title: '结果回传', status: 'wait', time: '--' },
      { title: '任务完成', status: 'wait', time: '--' }
    ],
    defects: [
      { id: 'D-001', type: '异物侵限', position: 'K13+260 右侧护栏', level: '中', status: '待处理' },
      { id: 'D-002', type: '支架锈蚀', position: 'K14+810 接触网支架', level: '低', status: '已记录' },
      { id: 'D-003', type: '桥面裂缝', position: 'K16+120 桥面板', level: '高', status: '待复核' }
    ],
    logs: [
      '09:20 调度中心创建巡检任务',
      '09:31 任务下发至 DJI-Matrice-RTK-01',
      '09:45 无人机起飞并进入预设航线',
      '10:18 当前巡检进度 68%，发现 3 条疑似缺陷'
    ]
  },
  {
    id: 1002,
    name: '车辆段屋面与排水沟巡检',
    code: 'TASK-20260702-002',
    routeName: '南湖车辆段 A/B 区',
    areaName: '屋面、排水沟、检修库外立面',
    deviceName: 'DJI-Mavic-03',
    pilot: '李工',
    status: 'pending',
    progress: 0,
    cleanStatus: '未清理',
    priority: '中',
    createdTime: '2026-07-02 10:05:00',
    startTime: '',
    endTime: '',
    rtspUrl: 'rtsp://127.0.0.1:8554/depot-roof',
    description: '检查车辆段屋面积水、排水沟堵塞和库房外立面破损情况。',
    resultSummary: { photos: 0, videos: 0, defects: 0, warnings: 0 },
    steps: [
      { title: '任务创建', status: 'success', time: '10:05' },
      { title: '任务下发', status: 'wait', time: '--' },
      { title: '无人机起飞', status: 'wait', time: '--' },
      { title: '巡检执行', status: 'wait', time: '--' },
      { title: '结果回传', status: 'wait', time: '--' },
      { title: '任务完成', status: 'wait', time: '--' }
    ],
    defects: [],
    logs: ['10:05 调度中心创建巡检任务，等待无人机空闲后下发']
  },
  {
    id: 1003,
    name: '区间隧道口边坡巡检',
    code: 'TASK-20260701-007',
    routeName: '3 号线北延段',
    areaName: '隧道口边坡与排水渠',
    deviceName: 'DJI-Matrice-RTK-02',
    pilot: '王工',
    status: 'completed',
    progress: 100,
    cleanStatus: '已清理',
    priority: '低',
    createdTime: '2026-07-01 15:10:00',
    startTime: '2026-07-01 15:30:00',
    endTime: '2026-07-01 16:08:00',
    rtspUrl: 'rtsp://127.0.0.1:8554/tunnel-slope',
    description: '对隧道口边坡、截水沟和防护网进行例行巡检。',
    resultSummary: { photos: 88, videos: 2, defects: 1, warnings: 0 },
    steps: [
      { title: '任务创建', status: 'success', time: '15:10' },
      { title: '任务下发', status: 'success', time: '15:18' },
      { title: '无人机起飞', status: 'success', time: '15:30' },
      { title: '巡检执行', status: 'success', time: '15:55' },
      { title: '结果回传', status: 'success', time: '16:02' },
      { title: '任务完成', status: 'success', time: '16:08' }
    ],
    defects: [
      { id: 'D-016', type: '防护网破损', position: '北延段 N3 隧道口', level: '中', status: '已派单' }
    ],
    logs: ['15:10 创建巡检任务', '15:30 无人机起飞', '16:02 巡检影像回传完成', '16:08 任务完成并归档']
  },
  {
    id: 1004,
    name: '站外附属设施夜间复查',
    code: 'TASK-20260701-009',
    routeName: '2 号线东城站周边',
    areaName: '风亭、出入口、站外围挡',
    deviceName: 'DJI-Mavic-Enterprise-02',
    pilot: '赵工',
    status: 'abnormal',
    progress: 42,
    cleanStatus: '待清理',
    priority: '高',
    createdTime: '2026-07-01 20:00:00',
    startTime: '2026-07-01 20:22:00',
    endTime: '',
    rtspUrl: 'rtsp://127.0.0.1:8554/station-night',
    description: '夜间复查站外附属设施照明、围挡和异物堆放情况。',
    resultSummary: { photos: 54, videos: 1, defects: 2, warnings: 4 },
    steps: [
      { title: '任务创建', status: 'success', time: '20:00' },
      { title: '任务下发', status: 'success', time: '20:10' },
      { title: '无人机起飞', status: 'success', time: '20:22' },
      { title: '巡检执行', status: 'error', time: '20:39' },
      { title: '结果回传', status: 'wait', time: '--' },
      { title: '任务完成', status: 'wait', time: '--' }
    ],
    defects: [
      { id: 'D-021', type: '照明异常', position: '东城站 B 出入口', level: '中', status: '待处理' },
      { id: 'D-022', type: '围挡倾斜', position: '东城站 2 号风亭', level: '高', status: '待复核' }
    ],
    logs: ['20:00 创建夜间复查任务', '20:22 无人机起飞', '20:39 视频链路波动，任务进入异常待确认状态']
  }
]
