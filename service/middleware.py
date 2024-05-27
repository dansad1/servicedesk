from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        register_url = reverse('register')
        
        # Проверка, аутентифицирован ли пользователь, и находится ли он не на странице входа или регистрации
        if not request.user.is_authenticated and not (
            request.path.startswith(settings.LOGIN_URL) or
            request.path.startswith(register_url)
        ):
            return redirect(settings.LOGIN_URL)
        
        response = self.get_response(request)
        return response