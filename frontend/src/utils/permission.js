import { dynamicRoutes } from '@/router/dynamicRoutes'

/**
 * 判断是否有权限访问路由
 */
function hasPermission(route, permissions) {
    const need = route.meta?.permission
    if (!need) return true
    return permissions.includes(need)
}

/**
 * 过滤路由
 */
export function filterAsyncRoutes(routes, permissions) {
    const res = []

    routes.forEach(route => {
        const tmp = { ...route }

        if (hasPermission(tmp, permissions)) {
            if (tmp.children) {
                tmp.children = filterAsyncRoutes(tmp.children, permissions)
            }
            res.push(tmp)
        }
    })

    return res
}

/**
 * 生成可访问路由
 */
export function generateRoutes(permissions) {
    return filterAsyncRoutes(dynamicRoutes, permissions)
}

/**
 * 根据角色生成侧边栏菜单
 */
export function getUserMenus(role) {
    const allMenus = dynamicRoutes
        .filter(route => {
            if (!route.meta?.permission) return true
            if (role === 'admin') return true
            const permissions = JSON.parse(localStorage.getItem('permissions') || '[]')
            return permissions.includes(route.meta.permission)
        })
        .map(route => ({
            path: route.path,
            title: route.meta?.title || route.name
        }))

    // 首页菜单
    return [
        { path: '/dashboard', title: '仪表盘' },
        ...allMenus
    ]
}