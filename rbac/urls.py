from django.urls import re_path
from rbac.views import permission

urlpatterns = [

    re_path(r'^menu/list/$', permission.menu_list, name='menu_list'), # rbac:menu_list
    re_path(r'^menu/add/$', permission.menu_add, name='menu_add'),
    re_path(r'^menu/edit/(?P<pk>\d+)/$', permission.menu_edit, name='menu_edit'),
    re_path(r'^menu/del/(?P<pk>\d+)/$', permission.menu_del, name='menu_del'),
    re_path(r'^permission/add/$', permission.permission_add, name='permission_add'),
    re_path(r'^permission/edit/(?P<pk>\d+)/$', permission.permission_edit, name='permission_edit'),
    re_path(r'^permission/del/(?P<pk>\d+)/$', permission.permission_del, name='permission_del'),

    re_path(r'^multi/permissions/$', permission.multi_permissions, name='multi_permissions'),

    re_path(r'^distribute/permissions/$', permission.distribute_permissions, name='distribute_permissions'),
    re_path(r'^role/list/$', permission.role_list, name='role_list'),
    re_path(r'^role/edit/(?P<pk>\d+)/$', permission.role_edit, name='role_edit'),
    re_path(r'^role/del/(?P<pk>\d+)/$', permission.role_del, name='role_del'),

]
