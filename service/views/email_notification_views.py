from absl.flags import ValidationError
from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.mail import send_mail, BadHeaderError, get_connection, EmailMessage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods

from servicedesk import settings
from service.forms.Email_forms import *
from ..models import EmailSettings, Event, NotificationSetting


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
@require_POST
def send_test_email(request):
    try:
        email_settings = EmailSettings.objects.last()
        print(email_settings)
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
        return JsonResponse({'success': False,
                             'error': f'Ошибка отправки письма: {e}, {email_settings.email_from, email_settings.login, email_settings.password}'})


def notification_overview(request):
    groups = Group.objects.all().order_by('id')
    events = Event.objects.all().order_by('id')
    settings_list = []

    for group in groups:
        group_settings = ['Да' if NotificationSetting.objects.filter(group=group, event=event).exists() else 'Нет' for event in events]
        settings_list.append((group, group_settings))

    return render(request, 'notifications/overview.html', {
        'groups': groups,
        'events': events,
        'settings_list': settings_list
    })