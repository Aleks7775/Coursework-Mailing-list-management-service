import os
import secrets
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView

from config.settings import EMAIL_HOST_USER
from users.forms import UserRegisterForms
from users.models import User

from django.contrib.auth.views import (PasswordResetView, PasswordResetDoneView,
                                       PasswordResetConfirmView, PasswordResetCompleteView,)


class RegisterView(CreateView):
    """Регистрация с подтверждением письма с токеном по почте """
    model = User
    form_class = UserRegisterForms
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f'http://{host}/users/email-confirm/{token}/'
        send_mail(
            subject='Подтверждение почты',
            message=f'Перейдите по ссылке для подтверждения регистрации {url}',
            from_email= os.getenv('EMAIL_HOST_USER'),
            recipient_list=[user.email]
        )
        return super().form_valid(form)


def email_verification(request, token):
    """Подтверждение токена из письма"""
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse('users:login'))


class UserListView(ListView):
    model = User
    fields = ['email', 'phone', 'country']
    template_name = "users/user_list.html"

    def get_queryset(self):
        user = self.request.user
        # print(user.get_all_permissions())
        if user.has_perm("users.view_user"):
            return User.objects.all()
        raise PermissionDenied


@permission_required('users.can_block_user')
def block_user(request, user_id):
    # Получаем пользователя по ID
    user = get_object_or_404(User, id=user_id)
    # Блокируем пользователя
    user.is_active = False
    user.save()
    return redirect('users:user_list')


class CustomPasswordResetView(PasswordResetView):
    template_name = "users/password_reset_form.html"
    email_template_name = "users/password_reset_email.html"
    subject_template_name = "users/password_reset_subject.html"
    success_url = "/users/password_reset/done/"


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "users/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "users/password_reset_confirm.html"
    success_url = "/users/reset/done/"


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "users/password_reset_complete.html"
