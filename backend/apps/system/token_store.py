"""
共享 Token 存储

所有认证相关的 token 存储统一在此模块管理，
避免循环引用和分散存储。
"""

# 全局 token 存储：token -> user_info dict
_TOKEN_STORE = {}
