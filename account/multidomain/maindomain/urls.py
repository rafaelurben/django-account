from django.urls import path

from . import views

app_name = "account-ext"

urlpatterns = [
    path("ext-login/<uuid:flow_uid>/", views.main_ext_login, name="ext-login"),
    path("ext-login-done", views.main_ext_login_done, name="ext-login-done"),
    path("ext-logout/<uuid:flow_uid>/", views.main_ext_logout, name="ext-logout"),
    path("ext-home/<uuid:flow_uid>/", views.main_ext_home, name="ext-home"),
    path("ext-home-done", views.main_ext_home_done, name="ext-home-done"),
]
