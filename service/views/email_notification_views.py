from absl.flags import ValidationError
from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.mail import send_mail, BadHeaderError, get_connection, EmailMessage
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from servicedesk import settings
from service.forms.Email_forms import *
from ..forms.Notification_forms import NotificationTemplateForm, NotificationSettingForm, StatusNotificationSettingForm
from ..models import EmailSettings, NotificationSetting, NotificationTemplate, Status
from ..variables import AVAILABLE_VARIABLES, EVENT_CHOICES
from django.template import Template, Context


def email_settings_view(request):
    if request.method == 'POST':
        form = EmailSettingsForm(request.POST)
        print(form.data)
        if form.is_valid():
            form.save()
            messages.success(request, f'Настройки электронной почты успешно сохранены.')
            return redirect('email_settings')
        else:
            # В случае ошибок, форма будет отображена снова с сохраненными данными
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')

    else:
        form = EmailSettingsForm()  # Пустая форма для GET запроса

    return render(request, 'settings/email_settings.html', {'form': form})


# Отправка тестового письма
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

        # Создание настраиваемого подключения на основе сохраненных настроек
        connection = get_connection(
            host=email_settings.server,
            port=email_settings.port,
            username=email_settings.login,
            password=email_settings.password,
            use_tls=email_settings.use_tls,
            use_ssl=email_settings.use_ssl,
            fail_silently=False,
        )

        # Создание и отправка электронного письма
        email = EmailMessage(
            subject="Тестовое письмо",
            body="Это тестовое сообщение от вашего Django-приложения.",
            from_email=email_settings.email_from,
            to=[test_email],
            connection=connection
        )
        email.send()

        return JsonResponse({'success': True})

    except Exception as e:  # Это поймает любые исключения, включая BadHeaderError
        return JsonResponse({'success': False, 'error': f'Ошибка отправки письма: {e}'})



def notification_table_overview(request):
    groups = Group.objects.all().order_by('id')
    templates = NotificationTemplate.objects.all()
    statuses = Status.objects.all()
    settings = []

    event_forms = []
    status_forms = []

    for group in groups:
        # Подготовка форм для событий
        for event_key, event_name in EVENT_CHOICES:
            setting = NotificationSetting.objects.filter(group=group, event=event_key).first()
            form = NotificationSettingForm(instance=setting, prefix=f"{group.id}_{event_key}")
            event_forms.append((group.id, event_key, form))
            settings.append({
                'group_id': group.id,
                'group_name': group.name,
                'event_key': event_key,
                'event_name': event_name,
                'email_template': setting.email_template.id if setting and setting.email_template else None,
                'push_template': setting.push_template.id if setting and setting.push_template else None,
                'sms_template': setting.sms_template.id if setting and setting.sms_template else None,
                'telegram_template': setting.telegram_template.id if setting and setting.telegram_template else None,
                'whatsapp_template': setting.whatsapp_template.id if setting and setting.whatsapp_template else None
            })

        # Подготовка форм для статусов
        for status in statuses:
            event_key = f"status_{status.id}"
            setting = NotificationSetting.objects.filter(group=group, event=event_key).first()
            form = StatusNotificationSettingForm(instance=setting, prefix=f"{group.id}_status_{status.id}")
            status_forms.append((group.id, status.id, form))

    return render(request, 'notifications/overview.html', {
        'groups': groups,
        'events': EVENT_CHOICES,
        'templates': templates,
        'settings': settings,
        'event_forms': event_forms,
        'statuses': statuses,
        'status_forms': status_forms,
    })

def update_notifications(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        group = get_object_or_404(Group, id=group_id)
        for event_key, _ in EVENT_CHOICES:
            form = NotificationSettingForm(request.POST, prefix=f"{group_id}_{event_key}")
            if form.is_valid():
                setting, created = NotificationSetting.objects.get_or_create(group=group, event=event_key)
                setting.email_template = form.cleaned_data['email_template']
                setting.push_template = form.cleaned_data['push_template']
                setting.sms_template = form.cleaned_data['sms_template']
                setting.telegram_template = form.cleaned_data['telegram_template']
                setting.whatsapp_template = form.cleaned_data['whatsapp_template']
                setting.save()

        for status in Status.objects.all():
            event_key = f"status_{status.id}"
            form = StatusNotificationSettingForm(request.POST, prefix=f"{group_id}_status_{status.id}")
            if form.is_valid():
                setting, created = NotificationSetting.objects.get_or_create(group=group, event=event_key)
                setting.email_template = form.cleaned_data['email_template']
                setting.push_template = form.cleaned_data['push_template']
                setting.sms_template = form.cleaned_data['sms_template']
                setting.telegram_template = form.cleaned_data['telegram_template']
                setting.whatsapp_template = form.cleaned_data['whatsapp_template']
                setting.save()

        return redirect('notification_overview')

def notification_template_list(request):
    templates = NotificationTemplate.objects.all()
    return render(request, 'notifications/notification_template_list.html', {'templates': templates})
def notification_template_create(request):
    if request.method == 'POST':
        form = NotificationTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('template_list')
    else:
        form = NotificationTemplateForm()
    context = {
        'form': form,
        'AVAILABLE_VARIABLES': AVAILABLE_VARIABLES  # Передаем переменные в шаблон
    }
    return render(request, 'notifications/notification_template_create.html', context)

def notification_template_edit(request, pk):
    template = get_object_or_404(NotificationTemplate, pk=pk)
    if request.method == 'POST':
        form = NotificationTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            return redirect('template_list')
    else:
        form = NotificationTemplateForm(instance=template)
    context = {
        'form': form,
        'template': template,
        'AVAILABLE_VARIABLES': AVAILABLE_VARIABLES  # Передаем переменные в шаблон
    }
    return render(request, 'notifications/notification_template_edit.html', context)

def notification_template_delete(request, pk):
    template = get_object_or_404(NotificationTemplate, pk=pk)
    template.delete()
    return redirect('template_list')
# utils.py

def render_template(template, context):
    """
    Заменяет переменные в шаблоне значениями из контекста.
    """

    t = Template(template)
    c = Context(context)
    return t.render(c)

def get_request_context(request):
    """
    Возвращает контекст с информацией о заявке и динамических полях, включая комментарии.
    """
    context = {
        'title': request.title,
        'description': request.description,
        'requester_username': request.requester.username if request.requester else '',
        'assignee_username': request.assignee.username if request.assignee else '',
        'company_name': request.company.name if request.company else '',
        'status_name': request.status.name if request.status else '',
        'created_at': request.created_at,
        'updated_at': request.updated_at,
        'priority_name': request.priority.name if request.priority else '',
        'request_type_name': request.request_type.name if request.request_type else '',
        'due_date': request.due_date,
        'attachment_url': request.attachment.url if request.attachment else '',
    }

    # Добавление динамических полей
    for field_value in request.field_values.all():
        if field_value.field_meta.field_type == 'comment':
            comments = context.get('comments', [])
            comments.append({
                'text': field_value.value_text,
                'author_username': field_value.value_requester.username if field_value.value_requester else '',
                'created_at': field_value.value_date,
                'attachment_url': field_value.value_file.url if field_value.value_file else '',
            })
            context['comments'] = comments
        else:
            context[field_value.field_meta.name] = field_value.get_value()

    return context
