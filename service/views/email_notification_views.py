from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from service.forms.Notification_forms import NotificationTemplateForm, NotificationSettingForm
from service.models import Request, Asset, Comment, CustomUser, Department, Status, NotificationTemplate, \
    NotificationSetting, FieldMeta
from django.core.mail import EmailMessage, get_connection
from .. import models
from ..forms.Email_forms import EmailSettingsForm
from ..models import EmailSettings
from django.db import models
from django.contrib.auth.models import Group
from django.db.models import Field, ForeignKey


EVENT_CHOICES = [
    ('create_request', 'Создание заявки'),
    ('update_request', 'Изменение полей заявки'),
    ('add_comment', 'Добавление комментария'),
    ('deadline_expiration', 'Истечение срока заявки'),
]

def generate_variables_from_model(model):
    """
    Генерирует переменные на основе полей модели Django.
    Включает как статические поля, так и связанные поля типа ForeignKey.
    """
    variables = {}
    for field in model._meta.get_fields():
        # Если поле является ForeignKey или OneToOneField
        if isinstance(field, models.ForeignKey) or isinstance(field, models.OneToOneField):
            variable_name = f"{field.name}_id"
            variable_desc = f"ID {field.verbose_name if field.verbose_name else field.name}"
            variables[variable_name] = variable_desc
        # Если поле является ManyToManyField
        elif isinstance(field, models.ManyToManyField):
            variable_name = f"{field.name}_ids"
            variable_desc = f"IDs связанных {field.verbose_name if field.verbose_name else field.name}"
            variables[variable_name] = variable_desc
        # Если это простое статическое поле
        elif isinstance(field, models.Field):
            variable_name = field.name
            variable_desc = field.verbose_name if field.verbose_name else field.name
            variables[variable_name] = variable_desc
        # Если поле представляет собой динамическое значение, например, через FieldMeta
        elif field.name == 'field_values':
            # Проходим по всем возможным типам полей в FieldMeta
            for field_meta in FieldMeta.objects.all():
                dynamic_var_name = f"{field_meta.name}_{field_meta.field_type}"
                dynamic_var_desc = f"Значение поля {field_meta.name} ({field_meta.field_type})"
                variables[dynamic_var_name] = dynamic_var_desc
        else:
            continue

    return variables

def get_context_for_notification(request=None, asset=None, comment=None, user=None, department=None):
    """
    Формирует контекст для уведомления на основе различных моделей.
    """
    context = {}

    if request:
        context.update(generate_variables_from_model(request))

    if asset:
        context.update(generate_variables_from_model(asset))

    if comment:
        context.update(generate_variables_from_model(comment))

    if user:
        context.update(generate_variables_from_model(user))

    if department:
        context.update(generate_variables_from_model(department))

    return context


def email_settings_view(request):
    if request.method == 'POST':
        form = EmailSettingsForm(request.POST)
        if form.is_valid():
            form.save()
            email_settings = EmailSettings.objects.last()
            form = EmailSettingsForm(instance=email_settings)
            return render(request, 'settings/email_settings.html', {'form': form, 'success': True})
    else:
        email_settings = EmailSettings.objects.last()
        form = EmailSettingsForm(instance=email_settings)

    return render(request, 'settings/email_settings.html', {'form': form})


@csrf_exempt
def send_test_email(request):
    try:
        email_settings = EmailSettings.objects.last()
        if not email_settings:
            return JsonResponse({'success': False, 'error': 'Настройки электронной почты не настроены'})

        test_email = request.POST.get('test_email_to')
        if not test_email:
            return JsonResponse({'success': False, 'error': 'Не указан адрес электронной почты для теста'})

        connection = get_connection(
            host=email_settings.server,
            port=email_settings.port,
            username=email_settings.login,
            password=email_settings.password,
            use_tls=email_settings.use_tls,
            use_ssl=email_settings.use_ssl,
            fail_silently=False,
        )

        email = EmailMessage(
            subject="Тестовое письмо",
            body="Это тестовое сообщение от вашего Django-приложения.",
            from_email=email_settings.email_from,
            to=[test_email],
            connection=connection
        )
        email.send()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Ошибка отправки письма: {e}'})


def notification_table_overview(request):
    groups = Group.objects.all().order_by('id')
    event_forms = []
    status_forms = []
    settings = []

    for group in groups:
        for event_key, event_name in EVENT_CHOICES:
            setting = NotificationSetting.objects.filter(group=group, event=event_key).first()
            form = NotificationSettingForm(instance=setting, prefix=f"{group.id}_{event_key}")
            event_forms.append((group.id, event_key, form))
            has_template = (
                setting and (
                    setting.email_template or
                    setting.push_template or
                    setting.sms_template or
                    setting.telegram_template or
                    setting.whatsapp_template
                )
            )
            settings.append({
                'group_id': group.id,
                'event_key': event_key,
                'has_template': has_template
            })

        for status in Status.objects.all():
            event_key = f"status_{status.id}"
            setting = NotificationSetting.objects.filter(group=group, event=event_key).first()
            form = NotificationSettingForm(instance=setting, prefix=f"{group.id}_{event_key}")
            status_forms.append((group.id, status.id, form))
            has_template = (
                setting and (
                    setting.email_template or
                    setting.push_template or
                    setting.sms_template or
                    setting.telegram_template or
                    setting.whatsapp_template
                )
            )
            settings.append({
                'group_id': group.id,
                'event_key': event_key,
                'status_id': status.id,
                'has_template': has_template
            })

    return render(request, 'notifications/overview.html', {
        'groups': groups,
        'event_forms': event_forms,
        'status_forms': status_forms,
        'events': EVENT_CHOICES,
        'statuses': Status.objects.all(),
        'settings': settings,
    })


def update_notifications(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        group = get_object_or_404(Group, id=group_id)

        # Обработка событий и статусов
        for event_key, _ in EVENT_CHOICES + [(f"status_{status.id}", status.name) for status in Status.objects.all()]:
            form = NotificationSettingForm(request.POST, prefix=f"{group_id}_{event_key}")
            if form.is_valid():
                setting, _ = NotificationSetting.objects.get_or_create(group=group, event=event_key)
                setting.email_template = form.cleaned_data['email_template']
                setting.push_template = form.cleaned_data['push_template']
                setting.sms_template = form.cleaned_data['sms_template']
                setting.telegram_template = form.cleaned_data['telegram_template']
                setting.whatsapp_template = form.cleaned_data['whatsapp_template']
                setting.save()

        return redirect('notification_overview')

def notification_template_create(request):
    available_variables = {
        'Request': generate_variables_from_model(Request),
        'Asset': generate_variables_from_model(Asset),
        'Comment': generate_variables_from_model(Comment),
        'User': generate_variables_from_model(CustomUser),
        'Department': generate_variables_from_model(Department),
    }

    form = NotificationTemplateForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('template_list')

    return render(request, 'notifications/notification_template_create.html', {
        'form': form,
        'AVAILABLE_VARIABLES': available_variables,
    })


def notification_template_edit(request, pk):
    template = get_object_or_404(NotificationTemplate, pk=pk)
    available_variables = {
        'Request': generate_variables_from_model(Request),
        'Asset': generate_variables_from_model(Asset),
        'Comment': generate_variables_from_model(Comment),
        'User': generate_variables_from_model(CustomUser),
        'Department': generate_variables_from_model(Department),
    }

    form = NotificationTemplateForm(request.POST or None, instance=template)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('template_list')

    return render(request, 'notifications/notification_template_edit.html', {
        'form': form,
        'AVAILABLE_VARIABLES': available_variables,
    })


def notification_template_list(request):
    templates = NotificationTemplate.objects.all()
    return render(request, 'notifications/notification_template_list.html', {'templates': templates})


def notification_template_delete(request, pk):
    template = get_object_or_404(NotificationTemplate, pk=pk)
    template.delete()
    return redirect('template_list')
