/**
 * 登录认证 API
 *
 * 当后端未启动时，自动 fallback 到本地 mock 数据，
 * 方便前端独立开发和调试。接入真实后端后删除 mock 部分即可。
 */
import request from './request'

// ── Mock 数据（后端未启动时的备用） ──────────────────────────
const MOCK_USERS = {
  admin: {
    id: 1,
    username: 'admin',
    nickname: '系统管理员',
    email: 'admin@uav.com',
    phone: '13800000000',
    role: 'admin'
  },
  user: {
    id: 2,
    username: 'user',
    nickname: '普通用户',
    email: 'user@uav.com',
    phone: '13800000001',
    role: 'user'
  }
}

const MOCK_PASSWORDS = { admin: 'admin123', user: 'user123' }

function mockLogin(username, password) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const user = MOCK_USERS[username]
      if (!user || MOCK_PASSWORDS[username] !== password) {
        reject(new Error('用户名或密码错误'))
        return
      }
      resolve({
        code: 200,
        message: '登录成功',
        data: {
          token: 'mock_token_' + Date.now(),
          user: { ...user }
        }
      })
    }, 300)
  })
}

// ── 正式 API ─────────────────────────────────────────────
export async function login(username, password) {
  let res
  try {
    res = await request({
      url: '/auth/login',
      method: 'post',
      data: { username, password }
    })
  } catch (err) {
    // 后端不可用（未启动、网络错误等）→ 降级到 mock
    console.warn('[login] 后端接口异常，降级使用 mock 数据', err?.message)
    const mockRes = await mockLogin(username, password)
    return mockRes.data
  }

  // 后端返回了响应，检查业务状态码
  // fail() 返回 HTTP 200 但 code!=200，需手动判断
  if (res.code !== 200) {
    throw new Error(res.message || '登录失败')
  }
  return res.data   // { token, user }
}

export async function logout() {
  try {
    await request({ url: '/auth/logout', method: 'post' })
  } catch {
    // 静默处理
  }
}

export async function getUserInfo() {
  try {
    const res = await request({ url: '/auth/userinfo', method: 'get' })
    return res.data
  } catch {
    // mock: 从 localStorage 恢复
    const saved = localStorage.getItem('user')
    if (saved) return JSON.parse(saved)
    return null
  }
}

export default { login, logout, getUserInfo }
