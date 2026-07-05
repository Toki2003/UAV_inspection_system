/**
 * 权限工具模块
 *
 * 提供权限层级展开、路由过滤、可访问路由生成等功能。
 * 核心设计：
 *   - 权限存储时仅保存叶子节点（如 role:view），父模块权限（role）通过 expandPermissions 自动推导
 *   - 路由过滤支持三种模式：permission 字段匹配、roles 角色限定、customCheck 自定义函数
 */
import { dynamicRoutes } from '@/router/dynamicRoutes'

/**
 * 权限层级映射表：父权限 -> 子权限数组
 * 用于根据叶子节点权限自动推导父模块权限
 * 注：role:assign / user:assign_role 为管理员专属，不参与父权限自动推导
 */
const PERMISSION_HIERARCHY = {
  'role': ['role:view', 'role:create', 'role:update', 'role:delete'],
  'user': ['user:view', 'user:create', 'user:update', 'user:delete'],
  'alert': ['alert:view', 'alert:handle', 'alert:delete'],
  'drone': ['drone:view', 'drone:control', 'drone:task']
}

/**
 * 根据叶子节点权限推导完整权限列表（包含父模块权限）
 * 设计意图：后端存储时仅保存叶子节点，前端展示时需要自动补全父模块权限
 * @param {Array} leafPermissions - 叶子节点权限列表
 * @returns {Array} 完整权限列表（包含推导出的父权限）
 */
export function expandPermissions(leafPermissions) {
  if (!Array.isArray(leafPermissions)) return []
  
  const expanded = new Set(leafPermissions)
  
  Object.entries(PERMISSION_HIERARCHY).forEach(([parentPerm, childPerms]) => {
    const hasChildPerm = childPerms.some(child => leafPermissions.includes(child))
    if (hasChildPerm) {
      expanded.add(parentPerm)
    }
  })
  
  return Array.from(expanded)
}

/**
 * 判断是否有权限访问路由
 * 支持两种模式：customCheck 自定义函数、permission 字段匹配
 */
function hasPermission(route, permissions) {
    const need = route.meta?.permission
    
    if (route.meta?.customCheck && typeof route.meta.customCheck === 'function') {
        const expandedPermissions = expandPermissions(permissions)
        return route.meta.customCheck(expandedPermissions)
    }
    
    if (!need) return true
    
    const expandedPermissions = expandPermissions(permissions)
    return expandedPermissions.includes(need)
}

/**
 * 递归过滤可访问的路由（根据权限码和角色）
 * @param {Array} routes - 待过滤的路由列表
 * @param {Array} permissions - 用户权限码列表
 * @returns {Array} 过滤后的可访问路由
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
 * 生成当前用户可访问的动态路由
 * @param {Array} permissions - 用户权限码列表
 * @returns {Array} 过滤后的可访问路由
 */
export function generateRoutes(permissions) {
    return filterAsyncRoutes(dynamicRoutes, permissions)
}
