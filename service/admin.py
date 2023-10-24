from django.contrib import admin
from .models import *
from django.contrib.auth.models import Permission

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
admin.site.register(CustomUser)
admin.site.register(UserRole)
admin.site.register(Request, RequestAdmin)
admin.site.register(Status)
admin.site.register(RequestType)
admin.site.register(Priority)
admin.site.register(PriorityDuration, PriorityDurationAdmin)
admin.site.register(StatusTransition, StatusTransitionAdmin)


# Permission Registration
admin.site.register(Permission)