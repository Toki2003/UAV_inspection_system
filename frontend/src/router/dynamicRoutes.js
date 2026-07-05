export const dynamicRoutes = [
    {
        path: '/system',
        name: 'SystemManage',
        component: () => import('@/views/SystemManage/index.vue'),
        meta: {
            title: '系统管理',
            // 有角色管理或用户管理的查看权限即可访问
            permission: null,
            customCheck: (permissions) => {
                return permissions.includes('role:view') || permissions.includes('user:view')
            }
        }
    },
    {
        path: '/alert',
        name: 'AlertManage',
        component: () => import('@/views/AlertManage/index.vue'),
        meta: {
            title: '告警管理',
            permission: 'alert:view'
        }
    },
    {
        path: '/drone-control',
        name: 'DroneControl',
        component: () => import('@/views/DroneControl/index.vue'),
        meta: {
            title: '无人机管控',
            permission: 'drone:view'
        }
    }
]