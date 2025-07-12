from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpRequest
from django.shortcuts import redirect
from django.utils.translation import gettext as _

from account.models import MultiDomainAuthFlow
from account.multidomain.altdomain.flow_helpers_alt import (
    initiate_multidomain_flow,
    complete_multidomain_flow,
)
from account.multidomain.altdomain.utils import login_with_any_backend
from account.multidomain.exceptions import AuthFlowException
from account.utils import account_entrypoint, pop_session_next, save_session_next


@account_entrypoint()
def alt_login(request: HttpRequest):
    return initiate_multidomain_flow(
        request,
        flow_type=MultiDomainAuthFlow.FlowType.LOGIN,
        alt_callback_viewname="account:login-callback",
        main_ext_viewname="ext-login",
    )


def alt_login_callback(request: HttpRequest):
    try:
        flow = complete_multidomain_flow(request, flow_type=MultiDomainAuthFlow.FlowType.LOGIN)

        login_with_any_backend(request, flow.user)
        messages.success(request, _("You have been successfully logged in."))
    except AuthFlowException:
        return redirect("account:login")  # try again

    return redirect(pop_session_next(request))


@account_entrypoint()
def alt_logout(request: HttpRequest):
    next_param = pop_session_next(request)
    logout(request)  # logout removes the user session, so the next param would be lost
    save_session_next(request, next_param)
    return initiate_multidomain_flow(
        request,
        flow_type=MultiDomainAuthFlow.FlowType.LOGOUT,
        alt_callback_viewname="account:logout-callback",
        main_ext_viewname="ext-logout",
    )


def alt_logout_callback(request: HttpRequest):
    try:
        complete_multidomain_flow(request, flow_type=MultiDomainAuthFlow.FlowType.LOGOUT)
        messages.success(request, _("You have been successfully logged out."))
    except AuthFlowException as e:
        messages.warning(request, str(e))

    return redirect(pop_session_next(request))


@account_entrypoint()
def alt_home(request: HttpRequest):
    return initiate_multidomain_flow(
        request,
        flow_type=MultiDomainAuthFlow.FlowType.ACCOUNT_HOME,
        alt_callback_viewname="account:home-callback",
        main_ext_viewname="ext-home",
    )


def alt_home_callback(request: HttpRequest):
    try:
        complete_multidomain_flow(request, flow_type=MultiDomainAuthFlow.FlowType.ACCOUNT_HOME)
    except AuthFlowException as e:
        messages.warning(request, str(e))

    return redirect(pop_session_next(request))
