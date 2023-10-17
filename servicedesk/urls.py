from django.urls import path, re_path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings  # Import the settings module
from django.conf.urls.static import static  # Import static for serving media files
from service.views.request_views import request_list, request_create, request_detail, request_update
from service.views.company_views import create_company
from service.views.profile_views import register, home, edit_profile, profile
from service.views.user_views import user_list

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
    path('request/request/<int:pk>/', request_detail, name='request_detail'),
    path('request/request/<int:pk>/update/', request_update, name='request_update'),
    path('profile/', profile, name='profile'),
    path('company/create_company/', create_company, name='create_company'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('users/', user_list, name='user_list'),  # Add this line
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
