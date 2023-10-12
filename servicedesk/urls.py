from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from service.views.company_views import *
from service.views.profile_views import *
from service.views.request_views import *
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),  # Важно, чтобы имя 'register' было в кавычках
    path('', home, name='home'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/requests/', request_list, name='request_list'),
    path('requests/request_create/', request_create, name='request_create'),
    path('request/request/<int:pk>/', request_detail, name='request_detail'),
    path('request/request/<int:pk>/update/', request_update, name='request_update'),
    path('profile/', profile, name='profile'),
    path('company/create_company/', create_company, name='create_company'),
]



