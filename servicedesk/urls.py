from django.urls import path, re_path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings  # Import the settings module
from django.conf.urls.static import static  # Import static for serving media files

import service.models
from service.views.request_views import request_list, request_create, request_detail_update
from service.views.company_views import company_create,company_edit,company_detail,company_list,create_department,create_subdepartment
from service.views.profile_views import register, home, edit_profile, profile, admin_section_view
from service.views.user_views import user_list,create_user_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('', home, name='home'),
    path('profile/edit/', edit_profile, name='edit_own_profile'),
    re_path(r'^profile/edit/(?P<pk>\d+)?/$', edit_profile, name='edit_profile'),
    path('profile/requests/', request_list, name='request_list'),
    path('requests/request_create/', request_create, name='request_create'),
    path('request/request/<int:pk>/', request_detail_update, name='request_detail_update'),
    path('profile/', profile, name='profile'),
    path('company/create_company/', company_create, name='create_company'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('user/', user_list, name='user_list'),
    path('admin_section/', admin_section_view, name='admin_section'),
    path('company/<int:pk>/', company_detail, name='company_detail'),
    path('company/<int:pk>/edit/', company_edit, name='company_edit'),
    path('company/', company_list, name='company_list'),
    path('create_user/', create_user_view, name='create_user'),
    path('company/<int:department_id>/create_subdepartment/', service.views.company_views.create_subdepartment, name='create_subdepartment'),
    path('company/<int:company_pk>/create_department/', service.views.company_views.create_department,name='create_department'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)







