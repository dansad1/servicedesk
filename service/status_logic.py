from .models import Status, StatusTransition
from django.db.models import Q

def set_default_status(request_instance):
    """
    Set the default status of 'Открыта' for new requests if it's not set,
    and make sure that the status is one that has transitions defined.
    """
    # Устанавливаем статус "Открыта" если статус не определен или его нет в переходах
    if not request_instance.status or not StatusTransition.objects.filter(
            Q(from_status=request_instance.status) | Q(to_status=request_instance.status)
    ).exists():
        default_status, created = Status.objects.get_or_create(name="Открыта")
        request_instance.status = default_status
        request_instance.save()

def check_and_update_request_status(request_instance, original_status=None):
    """
    Check conditions and update the status of the request accordingly.
    This function should be called after the request form is saved.
    """
    # Если статус был изменен в форме, проверяем, есть ли переходы для нового статуса
    if original_status and original_status != request_instance.status.name:
        if not StatusTransition.objects.filter(
                Q(from_status=request_instance.status) | Q(to_status=request_instance.status)
        ).exists():
            # Если нет переходов для нового статуса, возвращаем предыдущий статус
            previous_status = Status.objects.get(name=original_status)
            request_instance.status = previous_status
            request_instance.save()
            return
    # Вызываем функцию установки статуса по умолчанию
    set_default_status(request_instance)