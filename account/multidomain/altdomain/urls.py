from django.urls import path

from . import views

app_name = "account"

urlpatterns = [
    path("login", views.alt_login, name="login"),
    path("login-callback", views.alt_login_callback, name="login-callback"),
    path("logout", views.alt_logout, name="logout"),
    path("logout-callback", views.alt_logout_callback, name="logout-callback"),
    path("home", views.alt_home, name="home"),
    path("home-callback", views.alt_home_callback, name="home-callback"),
]
