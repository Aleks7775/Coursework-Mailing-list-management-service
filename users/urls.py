from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from users.views import RegisterView, email_verification, UserListView, block_user, deactivate_all_campaigns
from django.contrib.auth import views as auth_views

from users.apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page=''), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('email-confirm/<str:token>/', email_verification, name='email-confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('user/', UserListView.as_view(), name='user_list'),
    path('block_user/<int:user_id>/', block_user, name='block_user'),
    path('deactivate_all_campaigns/', deactivate_all_campaigns, name='deactivate_all_campaigns')

]
