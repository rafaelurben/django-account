import logging
import secrets

from django.contrib.auth import login, logout
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from account.conf import config
from account.models import MultiDomainAuthRequest
from account.utils import account_entrypoint, pop_session_next

SESSION_KEY_UID = 'account_alt_auth_uid'
SESSION_KEY_NONCE = 'account_alt_auth_nonce'

logger = logging.getLogger(__name__)


def _ensure_multidomain_config():
    if not config.MULTIDOMAIN_MAINDOMAIN_EXT_ACCOUNT_BASE_URL:
        raise ImproperlyConfigured(
            _("The authentication system is not configured for multi-domain support.")
        )


def _build_main_ext_url(view_name: str, *args, **kwargs) -> str:
    """
    Build a URL for the main domain's external authentication views.
    """
    base_url = config.MULTIDOMAIN_MAINDOMAIN_EXT_ACCOUNT_BASE_URL.rstrip('/')
    return base_url + reverse(view_name,
                              urlconf='account.multidomain.maindomain.urls',
                              args=args, kwargs=kwargs)


@account_entrypoint()
def alt_login(request: HttpRequest):
    _ensure_multidomain_config()

    ext_auth = MultiDomainAuthRequest.objects.create(
        callback_uri=request.build_absolute_uri(reverse('account:login-callback')),
        nonce=secrets.token_urlsafe(32)
    )

    request.session[SESSION_KEY_UID] = str(ext_auth.uid)
    request.session[SESSION_KEY_NONCE] = ext_auth.nonce

    return redirect(_build_main_ext_url('ext-login', ext_auth.uid))


def alt_login_callback(request: HttpRequest):
    stored_uid = request.session.get(SESSION_KEY_UID)
    stored_nonce = request.session.get(SESSION_KEY_NONCE)
    if not stored_uid or not stored_nonce:
        logger.info("No active authentication request found in session.")
        return redirect('account:login')  # try again

    try:
        ext_auth = MultiDomainAuthRequest.objects.get(uid=stored_uid)
    except MultiDomainAuthRequest.DoesNotExist:
        logger.info("Authentication request not found for UID: %s", stored_uid)
        return redirect('account:login')  # try again

    if ext_auth.nonce != stored_nonce:
        logger.warning("Nonce mismatch for UID: %s.", stored_uid)
        return redirect('account:login')  # try again

    if not ext_auth.is_recently_confirmed():
        logger.info("Authentication request not recently confirmed for UID: %s. State: %s", stored_uid, ext_auth.status)
        return redirect('account:login')  # try again

    ext_auth.status = MultiDomainAuthRequest.Status.COMPLETED
    ext_auth.timestamp_completed = timezone.now()
    ext_auth.save(update_fields=["status", "timestamp_completed"])

    # TODO: Better solution? Backend is not guaranteed to exist.
    login(request, ext_auth.user, backend='passkeys.backend.PasskeyModelBackend')

    request.session.pop(SESSION_KEY_UID, None)
    request.session.pop(SESSION_KEY_NONCE, None)

    return redirect(pop_session_next(request))


def alt_logout(request: HttpRequest):
    logout(request)
    # TODO: Also logout from main domain

    return redirect(request.GET.get('next', '/'))


@account_entrypoint()
def alt_home(request: HttpRequest):
    # TODO: Redirect to main domain
    return redirect("/")
