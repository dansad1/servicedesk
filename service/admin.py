from django.contrib import admin
from .models import Company, CustomUser, UserRole,Request,Status,Request_type
from django.contrib.auth.models import Permission

# Зарегистрируйте модели в административной панели
admin.site.register(Company)
admin.site.register(CustomUser)
admin.site.register(UserRole)
admin.site.register(Request)
admin.site.register(Status)
admin.site.register(Request_type)

# Регистрируем разрешения для ваших моделей
admin.site.register(Permission)
