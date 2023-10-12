from django import template

register = template.Library()

@register.filter(name='can_edit_request')
def can_edit_request(user, request):
    return user.is_authenticated and (user == request.requester or user == request.assignee or user.is_staff)
