from django.urls import path, re_path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static  # Import static for serving media files

import service.models
from service.views.chat_views import chat_view
from service.views.asset_type_views import *
from service.views.asset_views import create_asset, edit_asset, delete_asset, asset_list, get_attributes_by_asset_type
from service.views.attribute_views import attribute_create,  attribute_edit
from service.views.file_views import file_view
from service.views.request_field_views import request_field_edit, request_field_create, get_default_value_widget
from service.views.request_views import *
from service.views.company_views import company_create,company_edit,company_list,company_delete,department_create,department_delete,department_edit,subdepartment_create
from service.views.profile_views import *
from service.views.user_views import user_list,create_user_view,user_delete
from service.views.settings_views import types_list
from service.views.settings_views import *
from service.views.role_views import role_delete, role_edit
from service.views.email_notification_views import *
from service.views.perform_views import *
from service.views.chat_views import *
from service.views.user_views import CustomLoginView

urlpatterns = [

# URL-паттерны для регистрации
    path('admin/', admin.site.urls),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),

# URL-паттерны для профиля
    path('profile/edit/', edit_profile, name='edit_own_profile'),
    re_path(r'^profile/edit/(?P<pk>\d+)?/$', edit_profile, name='edit_profile'),
    path('users/delete/', user_delete, name='user_delete'),
    path('', profile, name='home'),
    path('profile/', profile, name='profile'),
    path('user/', user_list, name='user_list'),
    path('create_user/', create_user_view, name='create_user'),

    # URL-паттерны для заявок
    path('profile/requests/', request_list, name='request_list'),
    path('select_request_type/', select_request_type, name='select_request_type'),
    path('select_request_type/', select_request_type, name='select_request_type'),
    path('request/create/<int:request_type_id>/', request_create, name='request_create'),
    path('request/update/<int:pk>/', request_edit, name='request_edit'),
    path('requests/delete/', request_delete, name='request_delete'),
    path('request/<int:pk>/comment/', add_comment, name='add_comment'),
    path('ckeditor/', include('ckeditor_uploader.urls')),

    #Компании
    path('company/create/', company_create, name='create_company'),
    path('company/<int:pk>/edit/', company_edit, name='company_edit'),
    path('company/', company_list, name='company_list'),
    path('company/delete/', company_delete, name='company_delete'),

# Типы заявок
    path('request_type/create/', create_or_edit_request_type, name='create_request_type'),
    path('request_type/edit/<int:pk>/', create_or_edit_request_type, name='edit_request_type'),
    path('types_list/', types_list, name='types_list'),
    path('request-type/delete/<int:pk>/', delete_request_type, name='delete_request_type'),

    #Приоритеты заявок
    path('priority/create/', create_or_edit_priority, name='create_priority'),
    path('priority/edit/<int:pk>/', create_or_edit_priority, name='edit_priority'),
    path('priority/delete/<int:pk>/', delete_priority, name='delete_priority'),
    path('priority_list/', priority_list, name='priority_list'),

#Продолжительность заявок
    path('priority_duration/', priority_duration_list, name='priority_duration_list'),
    path('priority_duration/create/', create_or_edit_priority_duration, name='create_priority_duration'),
    path('priority_duration/edit/<int:pk>/', create_or_edit_priority_duration, name='edit_priority_duration'),

    #Статус заявок
    path('status/', status_list, name='status_list'),
    path('status/create/', create_or_edit_status, name='create_status'),
    path('status/<int:pk>/delete/', delete_status, name='delete_status'),
    path('status/edit/<int:pk>/', create_or_edit_status, name='edit_status'),


    #Переходы статусов
    path('status_transition/', status_transition, name='status_transition'),
    path('status_transition/delete/<int:pk>/', delete_status_transition, name='delete_status_transition'),

    #Панель настроек
    path('settings/', service.views.settings_views.settings_sidebar, name='settings_sidebar'),

    #Роли
    path('role/', service.views.role_views.role_list, name='role_list'),
    path('role/create/', service.views.role_views.role_create, name='role_create'),
    path('role/<int:group_id>/edit/', service.views.role_views.role_edit, name='role_edit'),
    path('role/<int:group_id>/delete/', service.views.role_views.role_delete, name='role_delete'),


    path('export_pdf/', service.views.request_views.export_requests_pdf, name='export_pdf'),
    path('email-settings/',service.views.email_notification_views.email_settings_view, name='email_settings'),
    path('send-test-email/', service.views.email_notification_views.send_test_email, name='send_test_email'),

    #Группы исполнителей
    path('groups/', performer_group_list, name='performer_group_list'),
    path('groups/create/', performer_group_create, name='performer_group_create'),
    path('groups/<int:pk>/update/', performer_group_update, name='performer_group_update'),
    path('groups/delete/', performer_group_delete, name='performer_group_delete'),

    #Активы
    path('assets/create/', create_asset, name='create_asset'),
    path('assets/edit/<int:pk>/', edit_asset, name='edit_asset'),
    path('assets/delete/', delete_asset, name='delete_asset'),
    path('assets/', asset_list, name='asset_list'),
    path('asset-types/<int:asset_type_id>/attributes/', get_attributes_by_asset_type,name='get_attributes_by_asset_type'),

    # Маршруты для типов активов
    path('asset_types/create/', asset_type_create, name='asset_type_create'),
    path('asset_types/edit/<int:pk>/', asset_type_edit, name='asset_type_edit'),
    path('asset_types/delete/', asset_type_delete, name='asset_type_delete'),
    path('asset_types/', asset_type_list, name='asset_type_list'),

    # Маршруты для атрибутов
    path('attributes/edit/<int:pk>/', attribute_edit, name='attribute_edit'),
    path('asset_types/<int:asset_type_id>/attributes/create/', service.views.attribute_views.attribute_create, name='attribute_create'),
    path('asset-types/<int:asset_type_id>/attributes/', get_attributes_by_asset_type, name='get_attributes_by_asset_type'),

# URL-паттерны для отделов
    path('department/<int:company_pk>/create_department/', department_create, name='department_create'),
    path('department/<int:department_id>/subdepartment_create/', subdepartment_create, name='subdepartment_create'),
    path('department/<int:pk>/edit/', department_edit, name='department_edit'),
    path('department/<int:pk>/delete/', department_delete, name='department_delete'),

# URL-паттерны для вложений
    path('file/<path:file_path>/', file_view, name='file_view'),
    path('file/', file_view, name='file_view'),

#чат
    path('chat/', chat_view, name='chat_view'),




    path('password_reset/', service.views.profile_views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', service.views.profile_views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', service.views.profile_views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', service.views.profile_views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

#уведомления
    path('notifications/', notification_table_overview, name='notification_overview'),
    path('notifications/detail/<int:group_id>/', notification_table_detail, name='notification_detail'),
    path('templates/<int:pk>/edit/', notification_template_edit, name='template_edit'),
    path('templates/', notification_template_list, name='template_list'),  # URL для списка шаблонов уведомлений
 path('templates/create/', notification_template_create, name='template_create'),
    path('templates/<int:pk>/delete/', notification_template_delete, name='template_delete'),

    #Поля заявок
    path('request_field/create/<int:request_type_id>/', request_field_create, name='request_field_create'),
    path('request_field/edit/<int:request_type_id>/<int:pk>/', request_field_edit, name='request_field_edit'),
    path('get_default_value_widget/', get_default_value_widget, name='get_default_value_widget'),

]




if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)







