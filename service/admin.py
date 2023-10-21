from django.contrib import admin
from .models import *
from django.contrib.auth.models import Permission

# Admin Actions
def make_high_priority(modeladmin, request, queryset):
    queryset.update(priority='High')

def make_normal_priority(modeladmin, request, queryset):
    queryset.update(priority='Normal')

def change_request_type_to_bug(modeladmin, request, queryset):
    bug_type, created = Request_type.objects.get_or_create(name='Bug')
    queryset.update(request_type=bug_type)

# Admin Classes
class RequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'requester', 'assignee', 'status', 'created_at', 'priority', 'request_type')
    list_filter = ('status', 'created_at', 'assignee', 'priority', 'request_type')
    search_fields = ('title', 'requester__username', 'assignee__username')
    actions = [make_high_priority, make_normal_priority, change_request_type_to_bug]

# Model Registrations
admin.site.register(Company)
admin.site.register(CustomUser)
admin.site.register(UserRole)
admin.site.register(Request, RequestAdmin)
admin.site.register(Status)
admin.site.register(RequestType)

# Permission Registration
admin.site.register(Permission)
