from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse


def change_password(request):
    """https://www.w3.org/TR/change-password-url/"""

    return redirect(reverse("account:password-change"))


def webauthn(request):
    """https://passkeys.dev/docs/advanced/related-origins/"""

    return JsonResponse({
        "origins": getattr(settings, "PASSKEY_RELATED_ORIGINS", []),
    })


def passkey_endpoints(request):
    """https://w3c.github.io/webappsec-passkey-endpoints/passkey-endpoints.html"""

    return JsonResponse({
        "enroll": request.build_absolute_uri(reverse("account:passkey-management")),
        "manage": request.build_absolute_uri(reverse("account:passkey-management")),
    })
