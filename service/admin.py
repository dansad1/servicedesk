from django.contrib import admin
from .models import *
from .models import CustomPermission, GroupPermission

def make_high_priority(modeladmin, request, queryset):
    high_priority = Priority.objects.get(name='High')
    queryset.update(priority=high_priority)

def make_normal_priority(modeladmin, request, queryset):
    normal_priority = Priority.objects.get(name='Normal')
    queryset.update(priority=normal_priority)

def change_request_type_to_bug(modeladmin, request, queryset):
    bug_type, created = RequestType.objects.get_or_create(name='Bug')
    queryset.update(request_type=bug_type)

# Admin Classes
class RequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'requester', 'assignee', 'status', 'created_at', 'priority', 'request_type')
    list_filter = ('status', 'created_at', 'assignee', 'priority', 'request_type')
    search_fields = ('title', 'requester__username', 'assignee__username')
    actions = [make_high_priority, make_normal_priority, change_request_type_to_bug]

class PriorityDurationAdmin(admin.ModelAdmin):
    list_display = ('request_type', 'priority', 'duration_in_hours')  # Изменил 'duration' на 'duration_in_hours'
    list_filter = ('request_type', 'priority')
class StatusTransitionAdmin(admin.ModelAdmin):
    list_display = ['from_status', 'to_status', 'get_allowed_groups']

    def get_allowed_groups(self, obj):
        return ', '.join([group.name for group in obj.allowed_groups.all()])

    get_allowed_groups.short_description = 'Allowed Groups'

# Model Registrations
admin.site.register(Company)
admin.site.register(Request, RequestAdmin)
admin.site.register(Status)
admin.site.register(RequestType)
admin.site.register(Priority)
admin.site.register(PriorityDuration, PriorityDurationAdmin)
admin.site.register(StatusTransition, StatusTransitionAdmin)

# Кастомный админ-класс для CustomUser
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'group')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'group__name')
    # Добавьте другие настройки по вашему усмотрению

# Проверка перед регистрацией GroupPermission
try:
    admin.site.unregister(GroupPermission)
except admin.sites.NotRegistered:
    pass

# Админ-классы для Permission и GroupPermission
class CustomPermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code_name']

class GroupPermissionAdmin(admin.ModelAdmin):
    list_display = ['group', 'get_custom_permission_display', 'access_level']

    def get_custom_permission_display(self, obj):
        return str(obj.custompermission)
    get_custom_permission_display.short_description = 'Custom Permission'
# Регистрация моделей
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(GroupPermission, GroupPermissionAdmin)
admin.site.register(CustomPermission, CustomPermissionAdmin)

# Регистрация и настройка стандартной модели Group, если это необходимо
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass
