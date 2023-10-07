from django.urls import path
from service import views
from django.contrib import admin
from django.contrib.auth import views as auth_views
from service import views as service_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', service_views.register, name='register'),
    path('', service_views.home, name='home'),
    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/create_company/', views.create_company, name='create_company'),
    path('profile/requests/', views.request_list, name='request_list'),
    path('profile/create_request/', views.create_request, name='create_request'),
    path('profile/request/<int:pk>/', views.request_detail, name='request_detail'),
    path('profile/request/<int:pk>/update/', views.request_update, name='request_update'),

]


