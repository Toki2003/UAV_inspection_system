/**
 * 用户管理 API（预留接口，当前使用 mock 数据）
 *
 * 以后接入真实后端时，删除 mock 部分，只保留 request 调用即可。
 */
import request from './request'

// ── Mock 数据 ─────────────────────────────────────────────
const mockUsers = [
  { id: 1, username: 'admin', nickname: '系统管理员', email: 'admin@uav.com', phone: '13800000000', role: 'admin' },
  { id: 2, username: 'user', nickname: '普通用户', email: 'user@uav.com', phone: '13800000001', role: 'user' }
]

function mockRequest(data, delay = 200) {
  return new Promise(resolve => {
    setTimeout(() => resolve({ code: 200, message: '操作成功', data }), delay)
  })
}

// ── 正式 API ─────────────────────────────────────────────

/** 获取用户列表 */
export async function getUserList() {
  try {
    const res = await request({ url: '/user/list', method: 'get' })
    return res.data
  } catch {
    console.warn('[user] 后端不可用，使用 mock 用户列表')
    return [...mockUsers]
  }
}

/** 创建用户 */
export async function createUser(data) {
  try {
    const res = await request({ url: '/user/create', method: 'post', data })
    return res.data
  } catch {
    const newUser = { id: Date.now(), ...data }
    mockUsers.push(newUser)
    return newUser
  }
}

/** 更新用户 */
export async function updateUser(id, data) {
  try {
    const res = await request({ url: `/user/${id}`, method: 'put', data })
    return res.data
  } catch {
    const idx = mockUsers.findIndex(u => u.id === id)
    if (idx >= 0) Object.assign(mockUsers[idx], data)
    return mockUsers[idx]
  }
}

/** 删除用户 */
export async function deleteUser(id) {
  try {
    await request({ url: `/user/delete/${id}`, method: 'delete' })
  } catch {
    const idx = mockUsers.findIndex(u => u.id === id)
    if (idx >= 0) mockUsers.splice(idx, 1)
  }
}

export default { getUserList, createUser, updateUser, deleteUser }
