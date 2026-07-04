// ================= Mock 系统管理数据 =================

export const mockUsers = [
    {
        id: 1,
        username: 'admin',
        real_name: '管理员',
        phone: '13800000000',
        role: { id: 1, name: '超级管理员' },
        role_name: '超级管理员',
        is_active: true,
        create_time: '2025-01-01 10:00:00'
    },
    {
        id: 2,
        username: 'user1',
        real_name: '普通用户',
        phone: '13900000000',
        role: { id: 2, name: '操作员' },
        role_name: '操作员',
        is_active: true,
        create_time: '2025-01-02 12:00:00'
    }
]

export const mockRoles = [
    {
        id: 1,
        name: '超级管理员',
        desc: '拥有所有权限',
        create_time: '2025-01-01 10:00:00'
    },
    {
        id: 2,
        name: '操作员',
        desc: '普通操作权限',
        create_time: '2025-01-02 10:00:00'
    }
]

export const mockMenus = [
    {
        id: 1,
        title: '系统管理',
        path: '/system',
        icon: 'setting',
        sort: 1,
        is_show: true,
        perms: ['admin'],   // ⭐ 加这一行（权限控制关键）
        create_time: '2025-01-01 10:00:00'
    },
    {
        id: 2,
        title: '告警管理',
        path: '/alert',
        icon: 'warning',
        sort: 2,
        is_show: true,
        perms: ['admin', 'user'],   // ⭐ 普通用户也能看
        create_time: '2025-01-01 11:00:00'
    }
]