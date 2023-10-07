from django.contrib import admin
from .models import Company, CustomUser, UserRole

# Зарегистрируйте модели в административной панели
admin.site.register(Company)
admin.site.register(CustomUser)
admin.site.register(UserRole)
