from service.forms.Email_forms import EmailSettingsForm
from service.models import EmailSettings
from django.core.mail import EmailMessage, get_connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404


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


def send_test_email():
    email_settings = EmailSettings.objects.last()
    if not email_settings:
        return "Настройки электронной почты не настроены"

    try:
        connection = get_connection(
            host=email_settings.server,
            port=email_settings.port,
            username=email_settings.login,
            password=email_settings.password,
            use_tls=email_settings.connection_type == 'tls',
            use_ssl=email_settings.connection_type == 'ssl',
            fail_silently=False,
        )

        email = EmailMessage(
            subject="Тестовое письмо",
            body="Это тестовое сообщение от вашего Django-приложения.",
            from_email=email_settings.email_from,
            to=["your_test_email@example.com"],
            connection=connection
        )
        email.send()
        return "Письмо успешно отправлено"
    except Exception as e:
        return f"Ошибка отправки письма: {e}"