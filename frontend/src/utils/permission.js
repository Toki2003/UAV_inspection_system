import { dynamicRoutes } from '@/router/dynamicRoutes'

/**
 * 权限层级映射表
 * 定义父权限和子权限的对应关系
 */
const PERMISSION_HIERARCHY = {
  'role': ['role:view', 'role:create', 'role:update', 'role:delete', 'role:assign'],
  'user': ['user:view', 'user:create', 'user:update', 'user:delete'],
  'alert': ['alert:view', 'alert:handle', 'alert:delete'],
  'drone': ['drone:view', 'drone:control', 'drone:task']
}

/**
 * 根据叶子节点权限推导完整权限列表（包含父模块权限）
 * @param {Array} leafPermissions - 叶子节点权限列表
 * @returns {Array} 完整权限列表（包含推导出的父权限）
 */
export function expandPermissions(leafPermissions) {
  if (!Array.isArray(leafPermissions)) return []
  
  const expanded = new Set(leafPermissions)
  
  // 遍历每个父模块，检查是否有子权限被选中
  Object.entries(PERMISSION_HIERARCHY).forEach(([parentPerm, childPerms]) => {
    // 如果有任何一个子权限被选中，则添加父权限
    const hasChildPerm = childPerms.some(child => leafPermissions.includes(child))
    if (hasChildPerm) {
      expanded.add(parentPerm)
    }
  })
  
  return Array.from(expanded)
}

/**
 * 判断是否有权限访问路由
 */
function hasPermission(route, permissions) {
    const need = route.meta?.permission
    
    // 如果有自定义检查函数，使用自定义逻辑
    if (route.meta?.customCheck && typeof route.meta.customCheck === 'function') {
        const expandedPermissions = expandPermissions(permissions)
        return route.meta.customCheck(expandedPermissions)
    }
    
    // 默认权限检查
    if (!need) return true
    
    // 使用扩展后的权限列表进行判断
    const expandedPermissions = expandPermissions(permissions)
    return expandedPermissions.includes(need)
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
 * @param {string} role - 用户角色
 * @param {Array} permissions - 权限列表（从 Pinia Store 传入）
 */
export function getUserMenus(role, permissions = []) {
    // 扩展权限列表（根据叶子节点推导父模块权限）
    const expandedPermissions = expandPermissions(permissions)
    
    const allMenus = dynamicRoutes
        .filter(route => {
            if (!route.meta?.permission && !route.meta?.customCheck) return true
            
            // 如果有自定义检查函数，使用自定义逻辑
            if (route.meta?.customCheck && typeof route.meta.customCheck === 'function') {
                return route.meta.customCheck(expandedPermissions)
            }
            
            return expandedPermissions.includes(route.meta.permission)
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