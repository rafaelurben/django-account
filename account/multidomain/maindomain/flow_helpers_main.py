import logging
import uuid

from django.http import HttpRequest
from django.utils import timezone
from django.utils.translation import gettext as _

from account.models import MultiDomainAuthFlow
from account.multidomain.exceptions import AuthFlowException

SESSION_KEY_PREFIX_UID = 'account_ext_auth_uid_'

logger = logging.getLogger(__name__)


def receive_multidomain_flow(request: HttpRequest,
                             flow_uid: uuid.UUID,
                             flow_type: MultiDomainAuthFlow.FlowType) -> MultiDomainAuthFlow:
    """
    Handle the initial reception of a multi-domain authentication flow.
    """
    try:
        flow = MultiDomainAuthFlow.objects.get(uid=flow_uid)
    except MultiDomainAuthFlow.DoesNotExist:
        logger.info("Authentication request not found for UID: %s", flow_uid)
        raise AuthFlowException(_("Invalid authentication flow. Please go back and try again."))

    if flow.flow_type != flow_type:
        logger.warning("Flow type mismatch for UID: %s. Expected: %s, Found: %s", flow_uid, flow_type, flow.flow_type)
        raise AuthFlowException(_("Authentication flow type mismatch. Please go back and try again."))

    if not flow.is_recently_created():
        logger.info("Authentication flow expired for UID: %s", flow_uid)
        raise AuthFlowException(_("Authentication flow expired. Please go back and try again."))

    flow.status = MultiDomainAuthFlow.Status.RECEIVED
    flow.timestamp_received = timezone.now()
    flow.save(update_fields=["status", "timestamp_received"])

    request.session[SESSION_KEY_PREFIX_UID + flow.flow_type] = str(flow.uid)

    return flow


def answer_multidomain_flow(request: HttpRequest,
                            flow_type: MultiDomainAuthFlow.FlowType,
                            confirm: bool,
                            user=None,
                            override_flow_uid: uuid.UUID = None) -> MultiDomainAuthFlow:
    """
    Answer the multi-domain authentication flow by confirming or denying it.
    """
    stored_uid = override_flow_uid or request.session.pop(SESSION_KEY_PREFIX_UID + flow_type, None)
    if not stored_uid:
        logger.info("No active authentication flow found in session.")
        raise AuthFlowException(_("No active authentication flow found. Please go back and try again."))

    try:
        flow = MultiDomainAuthFlow.objects.get(uid=stored_uid)
    except MultiDomainAuthFlow.DoesNotExist:
        logger.info("Authentication request not found for UID: %s", stored_uid)
        raise AuthFlowException(_("Authentication request not found for UID: {}").format(stored_uid))

    if flow.flow_type != flow_type:
        logger.warning("Flow type mismatch for UID: %s. Expected: %s, Found: %s", stored_uid, flow_type, flow.flow_type)
        raise AuthFlowException(_("Authentication flow type mismatch. Please go back and try again."))

    if flow.status != MultiDomainAuthFlow.Status.RECEIVED:
        logger.info("Authentication request in invalid state for UID: %s. State: %s", stored_uid, flow.status)
        raise AuthFlowException(_("Authentication request in invalid state. Please go back and try again."))

    flow.status = MultiDomainAuthFlow.Status.CONFIRMED if confirm else MultiDomainAuthFlow.Status.DENIED
    flow.timestamp_answered = timezone.now()
    if confirm and user:
        flow.user = user
    flow.save(update_fields=["status", "timestamp_answered", "user"])

    return flow
