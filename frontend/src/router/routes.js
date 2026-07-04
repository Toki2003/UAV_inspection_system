export const constantRoutes = [
    {
        path: '/login',
        component: () => import('@/views/Login.vue')
    },
    {
        path: '/',
        component: () => import('@/layout/index.vue'),
        children: []
    }
]