/**
 * v-permission 自定义指令
 *
 * 用法：v-permission="'role:create'" 传入权限码
 * 功能：根据当前用户权限控制元素的显示 / 隐藏。
 * 实现：通过 display:none 隐藏元素但保留在 DOM 中，权限恢复时可重新显示。
 * 权限判断使用 expandPermissions 自动推导父模块权限。
 */
import { useAppStore } from '@/store'
import { expandPermissions } from '@/utils/permission'

export default {
    mounted(el, binding) {
        checkPermission(el, binding)
    },
    updated(el, binding) {
        checkPermission(el, binding)
    }
}

/**
 * 检查权限并控制元素显示 / 隐藏
 * @param {HTMLElement} el - 指令绑定的 DOM 元素
 * @param {Object} binding - 指令绑定对象，value 为权限码字符串
 */
function checkPermission(el, binding) {
    const store = useAppStore()
    const value = binding.value

    if (!value) return

    const permissions = expandPermissions(store.permissions || [])
    const hasPermission = permissions.includes(value)

    if (!hasPermission) {
        // 隐藏元素但保留在 DOM 中，记录原始 display 值以便恢复
        el._originalDisplay = el.style.display
        el.style.display = 'none'
    } else {
        el.style.display = el._originalDisplay || ''
    }
}