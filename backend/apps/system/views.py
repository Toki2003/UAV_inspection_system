"""
权限管理模块 - 接口视图

提供菜单、角色、用户三部分的 CRUD 接口。
所有接口需登录访问（permission_classes = [IsAuthenticated]）。
"""

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Menu, Role, SysUser
from .serializers import MenuSerializer, RoleSerializer, SysUserSerializer
from .authentication import TokenAuthentication
from apps.inspection.responses import success


class MenuViewSet(viewsets.ModelViewSet):
    """
    菜单管理接口

    提供菜单 CRUD，用于角色权限分配和前端动态路由加载。
    接口前缀: /api/system/menus/
    """

    queryset = Menu.objects.all().order_by('sort')
    serializer_class = MenuSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    @action(methods=['get'], detail=False, url_path='current-user-menus')
    def current_user_menus(self, request):
        """
        获取当前用户的可见菜单

        前端登录后调用，动态渲染侧边栏导航。
        返回当前用户角色绑定的、且 is_show=True 的菜单，按 sort 排序。
        """
        login_user = request.user
        if not login_user.role:
            return success(data=[])
        menu_query = login_user.role.menus.filter(is_show=True).order_by('sort')
        ser = self.get_serializer(menu_query, many=True)
        return success(data=ser.data)


class RoleViewSet(viewsets.ModelViewSet):
    """
    角色管理接口

    管理系统角色，角色绑定菜单权限，用户分配角色使用。
    接口前缀: /api/system/roles/
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class SysUserViewSet(viewsets.ModelViewSet):
    """
    用户管理接口

    提供用户 CRUD 和角色分配功能。
    支持按角色筛选、按账号/姓名模糊搜索。
    接口前缀: /api/system/users/
    """

    queryset = SysUser.objects.all().order_by('-create_time')
    serializer_class = SysUserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role']
    search_fields = ['username', 'real_name']

    def list(self, request, *args, **kwargs):
        """查询用户列表，统一封装返回格式"""
        response = super().list(request, *args, **kwargs)
        return success(data=response.data)

    def retrieve(self, request, *args, **kwargs):
        """查询单条用户详情"""
        response = super().retrieve(request, *args, **kwargs)
        return success(data=response.data)

    def create(self, request, *args, **kwargs):
        """新增用户"""
        response = super().create(request, *args, **kwargs)
        return success('用户新增完成', data=response.data)

    def update(self, request, *args, **kwargs):
        """编辑用户信息、更换角色"""
        response = super().update(request, *args, **kwargs)
        return success('用户信息修改完成', data=response.data)

    def destroy(self, request, *args, **kwargs):
        """删除系统用户"""
        super().destroy(request, *args, **kwargs)
        return success('用户删除完成')