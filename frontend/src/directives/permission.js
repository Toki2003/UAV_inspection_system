import { useAppStore } from '@/store'
import { expandPermissions } from '@/utils/permission'

export default {
    mounted(el, binding) {
        checkPermission(el, binding)
    },
    updated(el, binding) {
        // 权限变化时重新检查
        checkPermission(el, binding)
    }
}

/**
 * 检查权限并控制元素显示/隐藏
 */
function checkPermission(el, binding) {
    const store = useAppStore()
    const value = binding.value

    if (!value) return

    // 获取扩展后的权限列表（包含父模块权限）
    const permissions = expandPermissions(store.permissions || [])

    const hasPermission = permissions.includes(value)

    if (!hasPermission) {
        // 隐藏元素但保留在DOM中，以便权限恢复时可以显示
        el._originalDisplay = el.style.display
        el.style.display = 'none'
    } else {
        // 恢复原始显示状态
        el.style.display = el._originalDisplay || ''
    }
}