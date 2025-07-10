from django.urls import path

from . import views

app_name = 'account'

urlpatterns = [
    path('login', views.alt_login, name="login"),
    path('login-callback', views.alt_login_callback, name="login-callback"),
    path('logout', views.alt_logout, name="logout"),
    path('home', views.alt_home, name="home"),
]
