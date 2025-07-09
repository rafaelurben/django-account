from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse

from account.conf import config


def change_password(request):
    """https://www.w3.org/TR/change-password-url/"""

    return redirect(reverse("account:password-change"))


def webauthn(request):
    """https://passkeys.dev/docs/advanced/related-origins/"""

    return JsonResponse({
        "origins": config.passkey_related_origins,
    })


def passkey_endpoints(request):
    """https://w3c.github.io/webappsec-passkey-endpoints/passkey-endpoints.html"""

    return JsonResponse({
        "enroll": request.build_absolute_uri(reverse("account:passkey-management")),
        "manage": request.build_absolute_uri(reverse("account:passkey-management")),
    })
