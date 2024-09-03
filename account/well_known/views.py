from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse


def change_password(request):
    "https://www.w3.org/TR/change-password-url/"

    return redirect(reverse("account:password-change"))

def webauthn(request):
    "https://github.com/w3c/webauthn/wiki/Explainer:-Related-origin-requests"

    return JsonResponse({
        "origins": getattr(settings, "PASSKEY_RELATED_ORIGINS", []),
    })
