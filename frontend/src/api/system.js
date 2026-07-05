/**
 * 系统管理 API
 *
 * 统一调用后端 /api/system/ 接口。
 */
import request from './request'

// ── 用户管理 ─────────────────────────────────────────────

/** 获取用户列表 */
export const getUserList = (params = {}) => {
  return request.get('/system/users/', { params })
}

/** 获取用户详情 */
export const getUserDetail = (id) => {
  return request.get(`/system/users/${id}/`)
}

/** 创建用户 */
export const createUser = (data) => {
  return request.post('/system/users/', data)
}

/** 更新用户 */
export const updateUser = (id, data) => {
  return request.put(`/system/users/${id}/`, data)
}

/** 删除用户 */
export const deleteUser = (id) => {
  return request.delete(`/system/users/${id}/`)
}

// ── 角色管理 ─────────────────────────────────────────────

/** 获取角色列表 */
export const getRoleList = () => {
  return request.get('/system/roles/')
}

/** 创建角色 */
export const createRole = (data) => {
  return request.post('/system/roles/', data)
}

/** 更新角色 */
export const updateRole = (id, data) => {
  return request.put(`/system/roles/${id}/`, data)
}

/** 删除角色 */
export const deleteRole = (id) => {
  return request.delete(`/system/roles/${id}/`)
}

/** 获取权限树 */
export const getPermissionTree = () => {
  return request.get('/system/roles/permission_tree/')
}

// ── 默认导出 ─────────────────────────────────────────────

export default {
  getUserList,
  getUserDetail,
  createUser,
  updateUser,
  deleteUser,

  getRoleList,
  createRole,
  updateRole,
  deleteRole,
  getPermissionTree
}
