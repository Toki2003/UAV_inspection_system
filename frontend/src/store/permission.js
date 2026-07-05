/**
 * 权限状态管理（Pinia Store）
 *
 * 职责：动态路由生成、菜单构建、权限变更事件总线。
 * 设计决策：
 *   - 路由过滤同时支持 roles 角色限定和 permission 权限码匹配
 *   - 权限变更通过 EventTarget 事件总线通知所有监听组件
 *   - routesAdded 标志防止重复添加路由
 */
import { defineStore } from 'pinia'
import { dynamicRoutes } from '@/router/dynamicRoutes'
import router from '@/router'
import { expandPermissions } from '@/utils/permission'

/** 权限变更事件总线（基于 EventTarget，解耦组件间通信） */
const permissionEventTarget = new EventTarget()

/**
 * 监听权限变更事件
 * @param {Function} callback - 回调函数
 * @returns {Function} 取消监听的清理函数
 */
export function onPermissionChange(callback) {
  permissionEventTarget.addEventListener('permission-change', callback)
  return () => {
    permissionEventTarget.removeEventListener('permission-change', callback)
  }
}

/** 发布权限变更事件，通知所有监听组件刷新 UI */
export function triggerPermissionChange() {
  permissionEventTarget.dispatchEvent(new CustomEvent('permission-change'))
}

export const usePermissionStore = defineStore('permission', {
    state: () => ({
        routesAdded: false,
        menus: []
    }),

    actions: {
        /**
         * 生成动态路由并构建菜单（唯一入口，幂等）
         * @param {string} role - 用户角色名称
         * @param {Array} permissions - 权限码列表
         */
        generateRoutes(role, permissions = []) {
            if (this.routesAdded) return

            // 过滤可访问路由
            const routes = this.filterRoutes(dynamicRoutes, role, permissions)

            // 将过滤后的路由动态注册到 router
            routes.forEach(route => {
                const cleanRoute = {
                    path: route.path,
                    name: route.name,
                    meta: route.meta,
                    component: route.component
                }
                router.addRoute('Layout', cleanRoute)
            })

            // 构建菜单：仪表盘 + 管理模块 + 个人中心（按角色区分）
            if (role === 'user') {
                // user 角色：仪表盘 + 我的任务 + 个人中心
                this.menus = [
                    { path: '/dashboard', title: '仪表盘' },
                    ...routes
                        .filter(r => r.path !== '/profile')
                        .map(r => ({ path: r.path, title: r.meta?.title || r.name })),
                    { path: '/profile', title: '个人中心' }
                ]
            } else {
                // admin / super_admin：仪表盘 + 管理模块 + 个人中心
                this.menus = [
                    { path: '/dashboard', title: '仪表盘' },
                    ...routes
                        .filter(r => r.path !== '/profile')
                        .map(r => ({ path: r.path, title: r.meta?.title || r.name })),
                    { path: '/profile', title: '个人中心' }
                ]
            }

            this.routesAdded = true
        },

        /**
         * 过滤可访问路由
         * - roles 字段：限定哪些角色可见（如 roles: ['user'] 表示仅 user 可见）
         * - permission 字段：需要对应权限码才可见
         * - customCheck：自定义权限检查函数
         */
        filterRoutes(routes, role, permissions) {
            const expandedPermissions = expandPermissions(permissions)
            
            return routes.filter(r => {
                if (r.meta?.roles && Array.isArray(r.meta.roles)) {
                    if (!r.meta.roles.includes(role)) return false
                }

                const perm = r.meta?.permission

                if (!perm && !r.meta?.customCheck) return true
                if (!Array.isArray(expandedPermissions)) return false

                if (r.meta?.customCheck && typeof r.meta.customCheck === 'function') {
                    return r.meta.customCheck(expandedPermissions)
                }

                return expandedPermissions.includes(perm)
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