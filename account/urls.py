from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from django.urls import reverse_lazy

from account.forms import LoginForm
from . import views
from .utils import account_entrypoint

#######################

app_name = 'account'

urlpatterns = [

    # Home

    path('',
         views.home,
         name="home"),

    # Leave

    path('leave',
         views.leave,
         name="leave"),

    # Management

    path('login',
         account_entrypoint()(auth_views.LoginView.as_view(
             template_name='account/login.html',
             redirect_authenticated_user=True,
             form_class=LoginForm,
         )),
         name="login"),
    path('logout',
         views.LogoutView.as_view(
             next_page=reverse_lazy("account:login")
         ),
         name='logout'),
    path('profile',
         views.profile,
         name="profile"),
    path('oauth-management',
         views.oauth_management,
         name="oauth-management"),
    path('passkey-management',
         views.passkey_management,
         name="passkey-management"),

    path('delete',
         views.delete_account,
         name="delete-account"),

    path('pwchange',
         account_entrypoint()(auth_views.PasswordChangeView.as_view(
             template_name="account/password-change.html",
             success_url=reverse_lazy("account:password-change-done"))),
         name="password-change"),
    path('pwchange/done',
         auth_views.PasswordChangeDoneView.as_view(
             template_name="account/password-change-done.html"),
         name="password-change-done"),

    path('pwreset',
         account_entrypoint()(auth_views.PasswordResetView.as_view(
             template_name="account/password-reset-form.html",
             email_template_name="account/password-reset-email.html",
             subject_template_name="account/password-reset-subject.html",
             success_url=reverse_lazy("account:password-reset-done"))),
         name="password-reset"),
    path('pwreset/done',
         auth_views.PasswordResetDoneView.as_view(
             template_name="account/password-reset-done.html"),
         name="password-reset-done"),

    path('pwreset/confirm/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(
             template_name="account/password-reset-confirm.html",
             success_url=reverse_lazy("account:password-reset-complete")),
         name="password-reset-confirm"),
    path('pwreset/complete',
         auth_views.PasswordResetCompleteView.as_view(
             template_name="account/password-reset-complete.html"),
         name="password-reset-complete"),

    # Errors

    re_path('.*', views.error404),
]
