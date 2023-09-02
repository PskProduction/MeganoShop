from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.views import View
from .accounts import cmd_create_buyer
from .forms import RegistrationForm, PasswordResetForm, PasswordNewForm
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from .models import PasswordResetCode


class RegistrationView(View):
    TEMPLATE_NAME = 'registration.jinja2'
    form_class = RegistrationForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.TEMPLATE_NAME, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['login']
            password = form.cleaned_data['password']
            user = cmd_create_buyer(name=name, email=email, password=password)
            if user is not None:
                # Успешная регистрация
                user = authenticate(username=email, password=password)
                if user is not None:
                    login(request, user)
                return redirect('/')
        else:
            # Форма не прошла валидацию, возвращаем с ошибками
            return render(request, self.TEMPLATE_NAME, {'form': form})
        return render(request, self.TEMPLATE_NAME)


class LoginView(View):
    TEMPLATE_NAME = 'login.jinja2'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, self.TEMPLATE_NAME, {'error_message': ''})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('/')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')  # Перенаправление на главную страницу после входа
        else:
            return render(request, self.TEMPLATE_NAME, {'error_message': 'Неверная почта или пароль.'})


class LogoutView(LogoutView):
    next_page = '/'


class PasswordResetView(View):
    TEMPLATE_NAME = 'password_reset.jinja2'
    form_class = PasswordResetForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.TEMPLATE_NAME, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = get_user_model().objects.get(email=email)

                # Удалить все неиспользованные коды сброса пароля
                PasswordResetCode.objects.filter(user=user).delete()

                if user.is_active:
                    password_reset_code = \
                        PasswordResetCode.objects.create_password_reset_code(user)
                    password_reset_code.send_password_reset_email()
                    return redirect('/')

            except get_user_model().DoesNotExist:
                pass

            content = {'alarm': "Don't work service."}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            return render(request, self.TEMPLATE_NAME, {'form': form})


class PasswordResetConfirm(View):
    TEMPLATE_NAME = 'password_reset_confirm.jinja2'
    form_class = PasswordNewForm

    def get(self, request):
        code = request.GET.get('code', '')

        try:
            password_reset_code = PasswordResetCode.objects.get(code=code)

            # Удалить код сброса пароля, если он старше срока действия
            delta = date.today() - password_reset_code.created_at.date()
            if delta.days > PasswordResetCode.objects.get_expiry_period():
                password_reset_code.delete()
                raise PasswordResetCode.DoesNotExist

            form = self.form_class()
            return render(request, self.TEMPLATE_NAME, {'form': form})
        except PasswordResetCode.DoesNotExist:
            return redirect('/')

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            code = request.GET.get('code', '')
            try:
                password_reset_code = PasswordResetCode.objects.get(code=code)
                password_reset_code.user.set_password(password)
                password_reset_code.user.save()

                # Delete password reset code just used
                password_reset_code.delete()

                return redirect('/')
            except PasswordResetCode.DoesNotExist:
                return redirect('/')

        else:
            return render(request, self.TEMPLATE_NAME, {'form': form})