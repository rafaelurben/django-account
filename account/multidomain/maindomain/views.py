import uuid

from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from account.models import MultiDomainAuthRequest

SESSION_KEY_UID = 'account_ext_auth_uid'


def main_ext_login(request: HttpRequest, request_uid: uuid.UUID):
    try:
        ext_auth = MultiDomainAuthRequest.objects.get(uid=request_uid)
    except MultiDomainAuthRequest.DoesNotExist:
        messages.error(request, _("Invalid authentication request. Please go back and try again."))
        return redirect('account:login')

    if not ext_auth.is_recently_created():
        messages.error(request, _("Authentication request expired. Please go back and try again."))
        return redirect('account:login')

    ext_auth.status = MultiDomainAuthRequest.Status.RECEIVED
    ext_auth.timestamp_received = timezone.now()
    ext_auth.save(update_fields=["status", "timestamp_received"])

    request.session[SESSION_KEY_UID] = str(ext_auth.uid)

    done_url = reverse('account-ext:ext-login-done')
    if request.user.is_authenticated:
        return redirect(done_url)

    return redirect(reverse('account:login') + f"?next={done_url}")


def main_ext_login_done(request: HttpRequest):
    stored_uid = request.session.get(SESSION_KEY_UID)
    if not stored_uid:
        messages.error(request, _("No active authentication request found. Please go back and try again."))
        return redirect('account:login')

    try:
        ext_auth = MultiDomainAuthRequest.objects.get(uid=stored_uid)
    except MultiDomainAuthRequest.DoesNotExist:
        messages.error(request, _("Authentication request not found. Please go back and try again."))
        return redirect('account:login')

    if ext_auth.status != MultiDomainAuthRequest.Status.RECEIVED:
        messages.error(request, _("Authentication request in invalid state. Please go back and try again."))
        return redirect('account:login')

    if request.user.is_authenticated:
        ext_auth.status = MultiDomainAuthRequest.Status.CONFIRMED
        ext_auth.user = request.user
    else:
        ext_auth.status = MultiDomainAuthRequest.Status.DENIED
        ext_auth.user = None
    ext_auth.timestamp_answered = timezone.now()
    ext_auth.save(update_fields=["status", "timestamp_answered", "user"])

    request.session.pop(SESSION_KEY_UID, None)

    return redirect(ext_auth.callback_uri)
