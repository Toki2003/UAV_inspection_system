import { defineStore } from 'pinia'
import { dynamicRoutes } from '@/router/dynamicRoutes'
import router from '@/router'

export const usePermissionStore = defineStore('permission', {
    state: () => ({
        routesAdded: false,
        menus: []
    }),

    actions: {
        /**
         * 生成动态路由 + 菜单（唯一入口）
         * @param {string} role - 用户角色
         * @param {Array} permissions - 权限列表
         */
        generateRoutes(role, permissions = []) {
            if (this.routesAdded) return

            // 1. 过滤路由
            const routes = this.filterRoutes(dynamicRoutes, role, permissions)

            // 2. 添加路由到 router
            routes.forEach(route => {
                const cleanRoute = {
                    path: route.path,
                    name: route.name,
                    meta: route.meta,
                    component: route.component
                }
                router.addRoute('Layout', cleanRoute)
            })

            // 3. 生成菜单
            this.menus = [
                { path: '/dashboard', title: '仪表盘' },
                ...routes.map(route => ({
                    path: route.path,
                    title: route.meta?.title || route.name
                }))
            ]

            this.routesAdded = true
        },

        /**
         * 过滤路由
         */
        filterRoutes(routes, role, permissions) {
            return routes.filter(r => {
                const perm = r.meta?.permission

                if (!perm) return true
                if (role === 'admin') return true
                if (!Array.isArray(permissions)) return false

                return permissions.includes(perm)
            })
        },

        /**
         * 重置状态（登出时调用）
         */
        reset() {
            this.routesAdded = false
            this.menus = []
        }
    }
})