from django.urls import path, re_path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings  # Import the settings module
from django.conf.urls.static import static  # Import static for serving media files

import service.models
from service.views.request_views import request_list, request_create, add_comment,update_request,export_requests_pdf
from service.views.company_views import company_create,company_edit,company_detail,company_list,create_department,create_subdepartment
from service.views.profile_views import register, home, edit_profile, profile
from service.views.user_views import user_list,create_user_view
from service.views.settings_views import types_list,create_or_edit_request_type,create_or_edit_priority,settings_sidebar
from service.views.settings_views import *
from service.views.role_views import role_delete,role_edit,role_create,role_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('', home, name='home'),
    path('profile/edit/', edit_profile, name='edit_own_profile'),
    re_path(r'^profile/edit/(?P<pk>\d+)?/$', edit_profile, name='edit_profile'),
    path('profile/requests/', request_list, name='request_list'),
    path('requests/create/', request_create, name='request_create'),
    path('requests/<int:pk>/update/', update_request, name='update_request'),
    path('requests/<int:pk>/comment/', add_comment, name='add_comment'),
    path('profile/', profile, name='profile'),
    path('company/create/', company_create, name='create_company'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('user/', user_list, name='user_list'),
    path('company/<int:pk>/', company_detail, name='company_detail'),
    path('company/<int:pk>/edit/', company_edit, name='company_edit'),
    path('company/', company_list, name='company_list'),
    path('create_user/', create_user_view, name='create_user'),
    path('company/<int:department_id>/create_subdepartment/', service.views.company_views.create_subdepartment, name='create_subdepartment'),
    path('company/<int:company_pk>/create_department/', service.views.company_views.create_department,name='create_department'),
    path('request_type/create/', create_or_edit_request_type, name='create_request_type'),
    path('request_type/edit/<int:pk>/', create_or_edit_request_type, name='edit_request_type'),
    path('types_list/', types_list, name='types_list'),
    path('priority/create/', create_or_edit_priority, name='create_priority'),
    path('priority/edit/<int:pk>/', create_or_edit_priority, name='edit_priority'),
    path('priority_list/', priority_list, name='priority_list'),
    path('priority_duration/', priority_duration_list, name='priority_duration_list'),
    path('priority_duration/create/', create_or_edit_priority_duration, name='create_priority_duration'),
    path('priority_duration/edit/<int:pk>/', create_or_edit_priority_duration, name='edit_priority_duration'),
    path('status/', status_list, name='status_list'),
    path('status/create/', create_or_edit_status, name='create_status'),
    path('status/edit/<int:pk>/', create_or_edit_status, name='edit_status'),
    path('status_transition/', status_transition, name='status_transition'),
    path('status_transition/delete/<int:pk>/', delete_status_transition, name='delete_status_transition'),
    path('settings/', service.views.settings_views.settings_sidebar, name='settings_sidebar'),
    path('role/', service.views.role_views.role_list, name='role_list'),
    path('role/create/', service.views.role_views.role_create, name='role_create'),
    path('role/<int:group_id>/edit/', service.views.role_views.role_edit, name='role_edit'),
    path('role/<int:group_id>/delete/', service.views.role_views.role_delete, name='role_delete'),
    path('export_pdf/', service.views.request_views.export_requests_pdf, name='export_pdf'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)







