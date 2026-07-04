/**
 * 登录认证 API
 *
 * 统一调用后端 /api/system/ 接口，不再使用 mock 数据。
 */
import request from './request'

/**
 * 用户登录
 * @param {string} username
 * @param {string} password
 * @returns {Promise<{token: string, user: object, permissions: Array}>}
 */
export async function login(username, password) {
  const res = await request({
    url: '/system/login',
    method: 'post',
    data: { username, password }
  })

  if (res.code !== 200) {
    throw new Error(res.message || '登录失败')
  }

  return res.data
}

/**
 * 用户登出
 */
export async function logout() {
  try {
    await request({
      url: '/system/logout',
      method: 'post'
    })
  } catch (e) {
    // ignore
  }
}

/**
 * 获取当前登录用户信息
 */
export async function getUserInfo() {
  const res = await request({
    url: '/system/userinfo',
    method: 'get'
  })
  return res.data
}

export default { login, logout, getUserInfo }
