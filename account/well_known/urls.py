"""
This url config must be included at /.well-known/, if it is included.
"""

from django.urls import path

from account.well_known import views

urlpatterns = [

    path('change-password',
         views.change_password),

    path('webauthn',
         views.webauthn),

    path('passkey-endpoints',
         views.passkey_endpoints),
]
