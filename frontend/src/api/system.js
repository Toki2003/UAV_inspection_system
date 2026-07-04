/**
 * 系统管理 API（MOCK 版本）
 * 用于前端独立开发，不依赖后端
 */

// ====================== MOCK 数据 ======================

import { mockUsers, mockRoles, mockMenus } from '@/mock/system'

// 模拟网络延迟
const delay = (data) =>
    new Promise(resolve => setTimeout(() => resolve(data), 300))

// ====================== 通用封装 ======================

function ok(data) {
    return {
        code: 200,
        message: 'success',
        data
    }
}

// ====================== 用户管理 ======================

export function getUserList() {
    return delay(
        ok({
            count: mockUsers.length,
            results: mockUsers
        })
    )
}

export function getUserDetail(id) {
    const user = mockUsers.find(u => u.id === id)
    return delay(ok(user || null))
}

export function createUser(data) {
    const newUser = {
        ...data,
        id: Date.now()
    }
    mockUsers.push(newUser)

    return delay(ok(newUser))
}

export function updateUser(id, data) {
    const index = mockUsers.findIndex(u => u.id === id)
    if (index !== -1) {
        mockUsers[index] = {
            ...mockUsers[index],
            ...data
        }
    }
    return delay(ok(mockUsers[index]))
}

export function deleteUser(id) {
    const index = mockUsers.findIndex(u => u.id === id)
    if (index !== -1) mockUsers.splice(index, 1)
    return delay(ok(true))
}

// ====================== 角色管理 ======================

export function getRoleList() {
    return delay(
        ok({
            count: mockRoles.length,
            results: mockRoles
        })
    )
}

export function createRole(data) {
    const newRole = {
        ...data,
        id: Date.now()
    }
    mockRoles.push(newRole)

    return delay(ok(newRole))
}

export function updateRole(id, data) {
    const index = mockRoles.findIndex(r => r.id === id)
    if (index !== -1) {
        mockRoles[index] = {
            ...mockRoles[index],
            ...data
        }
    }
    return delay(ok(mockRoles[index]))
}

export function deleteRole(id) {
    const index = mockRoles.findIndex(r => r.id === id)
    if (index !== -1) mockRoles.splice(index, 1)
    return delay(ok(true))
}

// ====================== 菜单管理 ======================

export function getMenuList() {
    return delay(
        ok({
            count: mockMenus.length,
            results: mockMenus
        })
    )
}

export function createMenu(data) {
    const newMenu = {
        ...data,
        id: Date.now()
    }
    mockMenus.push(newMenu)

    return delay(ok(newMenu))
}

export function updateMenu(id, data) {
    const index = mockMenus.findIndex(m => m.id === id)
    if (index !== -1) {
        mockMenus[index] = {
            ...mockMenus[index],
            ...data
        }
    }
    return delay(ok(mockMenus[index]))
}

export function deleteMenu(id) {
    const index = mockMenus.findIndex(m => m.id === id)
    if (index !== -1) mockMenus.splice(index, 1)
    return delay(ok(true))
}

// ====================== 默认导出 ======================

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

    getMenuList,
    createMenu,
    updateMenu,
    deleteMenu
}