
# Import Group model
from django.contrib.auth.models import Group

# Check if the user is in a particular group
def is_in_group(user, group_name):
    return Group.objects.get(name=group_name).user_set.filter(id=user.id).exists()

# 1. Viewing requests: Allow all users (No special code needed)

# 2. Editing requests
def can_edit_request(user, request):
    return (
        is_in_group(user, 'Администратор') or
        request.creator == user or
        request.executor == user
    )

# 3. Creating requests: Allow all users (No special code needed)

# 4. Creating users
def can_create_user(user):
    return is_in_group(user, 'Администратор')

# 5. Client-specific request visibility
def can_view_request(user, request):
    return (
        is_in_group(user, 'Администратор') or
        is_in_group(user, 'Исполнитель') or
        (is_in_group(user, 'Клиент') and request.company == user.company)
    )

# 6. Editing user profile
def can_edit_profile(user, profile_user):
    return (
        is_in_group(user, 'Администратор') or
        user == profile_user
    )
def can_edit_user_list(user):
    return is_in_group(user, 'Администратор')
def can_create_company(user):
    return is_in_group(user, 'Администратор')