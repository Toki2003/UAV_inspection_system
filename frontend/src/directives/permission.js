import { useAppStore } from '@/store'

export default {
    mounted(el, binding) {
        const store = useAppStore()

        const permissions = store.permissions || []
        const value = binding.value

        if (!value) return

        // admin 拥有所有权限（通配符）
        if (permissions.includes('admin')) return

        const hasPermission = permissions.includes(value)

        if (!hasPermission) {
            el.parentNode && el.parentNode.removeChild(el)
        }
    }
}