from django.urls import path
from service import views
from django.contrib import admin
from django.contrib.auth import views as auth_views
from service import views as service_views
from service.views import create_company
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', service_views.register, name='register'),
    path('', service_views.home, name='home'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/requests/', views.request_list, name='request_list'),
    path('requests/create_request/', views.create_request, name='create_request'),
    path('request/request/<int:pk>/', views.request_detail, name='request_detail'),
    path('request/request/<int:pk>/update/', views.request_update, name='request_update'),
    path('profile/', views.profile, name='profile'),
    path('company/create_company/', views.create_company, name='create_company'),

]




