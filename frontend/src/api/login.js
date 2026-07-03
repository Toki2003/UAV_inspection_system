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
  try {
    const res = await request({
      url: '/auth/login',
      method: 'post',
      data: { username, password }
    })
    return res.data          // { token, user }
  } catch (err) {
    // 后端不可用（未启动、500、404 等任何情况）→ 降级到 mock
    console.warn('[login] 后端接口异常，降级使用 mock 数据', err?.message)
    const res = await mockLogin(username, password)
    return res.data
  }
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
