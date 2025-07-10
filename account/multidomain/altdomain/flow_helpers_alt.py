import logging
import secrets

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from account.conf import config
from account.models import MultiDomainAuthFlow
from account.multidomain.exceptions import AuthFlowException

SESSION_KEY_PREFIX_UID = 'account_alt_auth_uid_'
SESSION_KEY_PREFIX_NONCE = 'account_alt_auth_nonce_'

GENERIC_AUTH_FLOW_EXCEPTION_MESSAGE = _("Something went wrong with the authentication flow. Please try again.")

logger = logging.getLogger(__name__)


def initiate_multidomain_flow(request: HttpRequest,
                              flow_type: MultiDomainAuthFlow.FlowType,
                              alt_callback_viewname: str,
                              main_ext_viewname: str) -> HttpResponse:
    """
    Initialize a new multi-domain authentication flow.
    """
    if not config.MULTIDOMAIN_MAINDOMAIN_EXT_ACCOUNT_BASE_URL:
        raise ImproperlyConfigured(
            _("The authentication system is not configured for multi-domain support.")
        )

    flow = MultiDomainAuthFlow.objects.create(
        flow_type=flow_type,
        callback_uri=request.build_absolute_uri(reverse(alt_callback_viewname)),
        nonce=secrets.token_urlsafe(32)
    )

    request.session[SESSION_KEY_PREFIX_UID + flow_type] = str(flow.uid)
    request.session[SESSION_KEY_PREFIX_NONCE + flow_type] = flow.nonce

    ext_base_url = config.MULTIDOMAIN_MAINDOMAIN_EXT_ACCOUNT_BASE_URL.rstrip('/')
    url = ext_base_url + reverse(main_ext_viewname,
                                 urlconf='account.multidomain.maindomain.urls',
                                 args=[flow.uid])

    return redirect(url)


def complete_multidomain_flow(request: HttpRequest,
                              flow_type: MultiDomainAuthFlow.FlowType) -> MultiDomainAuthFlow:
    """
    Complete the multi-domain authentication flow by verifying the session and flow state.
    """

    stored_uid = request.session.pop(SESSION_KEY_PREFIX_UID + flow_type, None)
    stored_nonce = request.session.pop(SESSION_KEY_PREFIX_NONCE + flow_type, None)
    if not stored_uid or not stored_nonce:
        logger.info("No active authentication flow found in session.")
        raise AuthFlowException(_("No active authentication flow found."))

    try:
        flow = MultiDomainAuthFlow.objects.get(uid=stored_uid)
    except MultiDomainAuthFlow.DoesNotExist:
        logger.info("Authentication request not found for UID: %s", stored_uid)
        raise AuthFlowException(_("Authentication request not found for UID: {}").format(stored_uid))

    if flow.flow_type != flow_type:
        logger.warning("Flow type mismatch for UID: %s. Expected: %s, Found: %s", stored_uid, flow_type, flow.flow_type)
        raise AuthFlowException(GENERIC_AUTH_FLOW_EXCEPTION_MESSAGE)

    if flow.nonce != stored_nonce:
        logger.warning("Nonce mismatch for UID: %s.", stored_uid)
        raise AuthFlowException(GENERIC_AUTH_FLOW_EXCEPTION_MESSAGE)

    if not flow.is_recently_confirmed():
        logger.info("Authentication request not recently confirmed for UID: %s. State: %s", stored_uid, flow.status)
        raise AuthFlowException(GENERIC_AUTH_FLOW_EXCEPTION_MESSAGE)

    flow.status = MultiDomainAuthFlow.Status.COMPLETED
    flow.timestamp_completed = timezone.now()
    flow.save(update_fields=["status", "timestamp_completed"])

    return flow
