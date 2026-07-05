/**
 * 动态路由配置
 *
 * 定义所有需要权限控制的路由，由 permission store 根据用户权限动态注册。
 * 路由 meta 字段说明：
 *   - title: 菜单显示名称
 *   - permission: 所需权限码（如 'alert:view'），无则不检查
 *   - customCheck: 自定义权限检查函数，用于复合条件判断
 *   - roles: 角色白名单，限定哪些角色可见
 */
export const dynamicRoutes = [
    {
        path: '/system',
        name: 'SystemManage',
        component: () => import('@/views/SystemManage/index.vue'),
        meta: {
            title: '系统管理',
            // 有角色管理或用户管理的查看权限即可访问系统管理页
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
            title: '主控台',
            permission: 'drone:view'
        }
    },
    // 公共路由（所有角色可见）
    {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/Profile/index.vue'),
        meta: {
            title: '个人中心'
        }
    },
    // user 角色专属路由
    {
        path: '/my-tasks',
        name: 'MyTasks',
        component: () => import('@/views/MyTasks/index.vue'),
        meta: {
            title: '我的任务',
            roles: ['user']
        }
    }
]
