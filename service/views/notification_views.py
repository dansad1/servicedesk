from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from service.forms.Notification_forms import NotificationTemplateForm, NotificationSettingForm
from service.models import Request, Asset, Comment, CustomUser, Department, Status, NotificationTemplate, \
    NotificationSetting, RequestFieldMeta
from django.core.mail import EmailMessage, get_connection
from .. import models
from ..forms.Email_forms import EmailSettingsForm
from ..models import EmailSettings
from django.db import models
from django.contrib.auth.models import Group
from django.db.models import Field, ForeignKey
from service.views.role_views import determine_users_for_functional_role


EVENT_CHOICES = [
    ('create_request', 'Создание заявки'),
    ('update_request', 'Изменение полей заявки'),
    ('add_comment', 'Добавление комментария'),
    ('deadline_expiration', 'Истечение срока заявки'),
]
PREDEFINED_CONSTRUCTIONS = {
    "if": "{% if condition %} ... {% endif %}",
    "for": "{% for item in items %} ... {% endfor %}",
}



def generate_variables_from_model(model):
    """
    Генерирует переменные на основе полей модели Django.
    Включает как статические поля, так и связанные поля типа ForeignKey.
    """
    variables = {}

    # Проходим по всем полям модели
    for field in model._meta.get_fields():
        # Если поле является ForeignKey или OneToOneField
        if isinstance(field, models.ForeignKey) or isinstance(field, models.OneToOneField):
            variable_name = f"{field.name}_id"
            variable_desc = f"ID {field.verbose_name if field.verbose_name else field.name.capitalize()}"
            variables[variable_name] = variable_desc

        # Если поле является ManyToManyField
        elif isinstance(field, models.ManyToManyField):
            variable_name = f"{field.name}_ids"
            variable_desc = f"IDs связанных {field.verbose_name if field.verbose_name else field.name.capitalize()}"
            variables[variable_name] = variable_desc

        # Если это простое статическое поле
        elif isinstance(field, models.Field):
            variable_name = field.name
            variable_desc = field.verbose_name.capitalize() if field.verbose_name else field.name.capitalize()
            variables[variable_name] = variable_desc

        # Если поле представляет собой динамическое значение, например, через FieldMeta
        elif field.name == 'field_values':
            # Проходим по всем возможным типам полей в FieldMeta
            for field_meta in RequestFieldMeta.objects.all():
                dynamic_var_name = f"{field_meta.name}_{field_meta.field_type}"
                dynamic_var_desc = f"Значение поля {field_meta.name.capitalize()} ({field_meta.field_type.capitalize()})"
                # Убедитесь, что динамическая переменная не пересекается с существующими
                if dynamic_var_name not in variables:
                    variables[dynamic_var_name] = dynamic_var_desc

        else:
            continue

    return variables


def get_context_for_notification(request=None, asset=None, comment=None, user=None, department=None):
    """
    Формирует контекст для уведомления на основе различных моделей, включая кастомные поля.
    """
    context = {}

    if request:
        # Стандартные переменные для модели Request
        context.update(generate_variables_from_model(request))

        # Добавление значений динамических полей заявки
        field_values = request.get_field_values()
        context.update(field_values)

    if asset:
        context.update(generate_variables_from_model(asset))

    if comment:
        context.update(generate_variables_from_model(comment))

    if user:
        context.update(generate_variables_from_model(user))

    if department:
        context.update(generate_variables_from_model(department))

    return context




def notification_table_overview(request):
    event_forms = []
    settings = []

    # Работа с функциональными ролями
    for role_key, role_name in NotificationSetting.ROLE_CHOICES:
        for event_key, event_name in EVENT_CHOICES:
            setting = NotificationSetting.objects.filter(functional_role=role_key, event=event_key).first()
            form = NotificationSettingForm(instance=setting, prefix=f"{role_key}_{event_key}")
            event_forms.append((role_key, event_key, form))
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
                'role_key': role_key,
                'event_key': event_key,
                'has_template': has_template
            })

    return render(request, 'notifications/overview.html', {
        'event_forms': event_forms,
        'events': EVENT_CHOICES,
        'settings': settings,
        'roles': NotificationSetting.ROLE_CHOICES,
    })


def update_notifications(request):
    if request.method == 'POST':
        role_key = request.POST.get('role_key')

        # Обработка событий
        for event_key, _ in EVENT_CHOICES:
            form = NotificationSettingForm(request.POST, prefix=f"{role_key}_{event_key}")
            if form.is_valid():
                setting, _ = NotificationSetting.objects.get_or_create(functional_role=role_key, event=event_key)
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
        'PREDEFINED_CONSTRUCTIONS': PREDEFINED_CONSTRUCTIONS,  # Добавляем предопределенные конструкции в контекст

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
        'PREDEFINED_CONSTRUCTIONS': PREDEFINED_CONSTRUCTIONS,  # Добавляем предопределенные конструкции в контекст

    })


def notification_template_list(request):
    templates = NotificationTemplate.objects.all()
    return render(request, 'notifications/notification_template_list.html', {'templates': templates})


def notification_template_delete(request, pk):
    template = get_object_or_404(NotificationTemplate, pk=pk)
    template.delete()
    return redirect('template_list')
def handle_event(event, context):
    """
    Обрабатывает событие и отправляет уведомления на основе настроек.
    """
    # Получаем все настройки уведомлений для данного события
    notification_settings = NotificationSetting.objects.filter(event=event)

    for setting in notification_settings:
        # Формируем уведомление в зависимости от типа (email, sms, push и т.д.)
        if setting.email_template:
            send_email_notification(setting.email_template, context)
        if setting.sms_template:
            send_sms_notification(setting.sms_template, context)
        if setting.push_template:
            send_push_notification(setting.push_template, context)
        if setting.telegram_template:
            send_telegram_notification(setting.telegram_template, context)
        if setting.whatsapp_template:
            send_whatsapp_notification(setting.whatsapp_template, context)




def send_email_notification(request, event, instance_id):
    """
        Отправляет SMS уведомление.
        """
    instance = get_object_or_404(Request, id=instance_id)
    context = get_context_for_notification(request=instance)

    settings = NotificationSetting.objects.filter(event=event)
    if not settings.exists():
        return JsonResponse({'success': False, 'error': 'Настройки уведомлений для данного события не найдены.'})

    for setting in settings:
        users = determine_users_for_functional_role(setting.functional_role, instance)
        for user in users:
            context['user'] = user  # Добавляем пользователя в контекст

            # Формируем заголовок и тело письма
            subject = setting.email_template.subject.format(**context)
            body = setting.email_template.body.format(**context)

            try:
                email_settings = EmailSettings.objects.last()
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
                    subject=subject,
                    body=body,
                    from_email=email_settings.email_from,
                    to=[user.email],
                    connection=connection
                )
                email.send()

            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Ошибка отправки письма: {e}'})

    return JsonResponse({'success': True, 'message': 'Email уведомления отправлены.'})

def send_sms_notification(template, context):
    """
    Отправляет SMS уведомление.
    """
    # Здесь будет логика отправки SMS
    pass

def send_push_notification(template, context):
    """
    Отправляет Push уведомление.
    """
    # Здесь будет логика отправки Push уведомления
    pass

def send_telegram_notification(template, context):
    """
    Отправляет Telegram уведомление.
    """
    # Здесь будет логика отправки уведомления через Telegram
    pass

def send_whatsapp_notification(template, context):
    """
    Отправляет WhatsApp уведомление.
    """
    # Здесь будет логика отправки уведомления через WhatsApp
    pass
