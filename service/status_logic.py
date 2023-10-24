from django.shortcuts import get_object_or_404
from .models import Request, Status
from django.utils import timezone

def update_request_status(request_instance):
    """Update the status of a Request instance based on certain conditions."""
    # Update request status based on form data
    if request_instance.assignee:
        status_in_work, created = Status.objects.get_or_create(name="В работе")
        request_instance.status = status_in_work
    else:
        status_opened, created = Status.objects.get_or_create(name="Открыта")
        request_instance.status = status_opened

    # Update the 'updated_at' timestamp
    request_instance.updated_at = timezone.now()

    request_instance.save()