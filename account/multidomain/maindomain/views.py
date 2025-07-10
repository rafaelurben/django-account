import uuid

from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse

from account.models import MultiDomainAuthFlow
from account.multidomain.exceptions import AuthFlowException
from account.multidomain.maindomain.flow_helpers_main import receive_multidomain_flow, answer_multidomain_flow


def main_ext_login(request: HttpRequest, flow_uid: uuid.UUID):
    try:
        receive_multidomain_flow(
            request,
            flow_uid=flow_uid,
            flow_type=MultiDomainAuthFlow.FlowType.LOGIN,
        )
    except AuthFlowException as e:
        messages.error(request, str(e))
        return redirect('account:login')

    done_url = reverse('account-ext:ext-login-done')
    if request.user.is_authenticated:
        return redirect(done_url)

    return redirect(reverse('account:login') + f"?next={done_url}")


def main_ext_login_done(request: HttpRequest):
    try:
        flow = answer_multidomain_flow(
            request,
            flow_type=MultiDomainAuthFlow.FlowType.LOGIN,
            confirm=request.user.is_authenticated,
            user=request.user if request.user.is_authenticated else None,
        )
    except AuthFlowException as e:
        messages.error(request, str(e))
        return redirect('account:login')

    return redirect(flow.callback_uri)


def main_ext_logout(request: HttpRequest, flow_uid: uuid.UUID):
    try:
        receive_multidomain_flow(
            request,
            flow_uid=flow_uid,
            flow_type=MultiDomainAuthFlow.FlowType.LOGOUT,
        )
        logout(request)
        flow = answer_multidomain_flow(
            request,
            flow_type=MultiDomainAuthFlow.FlowType.LOGOUT,
            confirm=True,  # Always confirm logout
            override_flow_uid=flow_uid,  # Logout clear the session, so we need to use the provided flow_uid
        )
    except AuthFlowException as e:
        messages.error(request, str(e))
        return redirect('account:logout')

    return redirect(flow.callback_uri)


def main_ext_home(request: HttpRequest, flow_uid: uuid.UUID):
    try:
        receive_multidomain_flow(
            request,
            flow_uid=flow_uid,
            flow_type=MultiDomainAuthFlow.FlowType.ACCOUNT_HOME,
        )
    except AuthFlowException as e:
        messages.warning(request, str(e))

    done_url = reverse('account-ext:ext-home-done')
    return redirect(reverse('account:home') + f"?next={done_url}")


def main_ext_home_done(request: HttpRequest):
    try:
        flow = answer_multidomain_flow(
            request,
            flow_type=MultiDomainAuthFlow.FlowType.ACCOUNT_HOME,
            confirm=True,  # Always confirm account home
        )
    except AuthFlowException as e:
        messages.error(request, str(e))
        return redirect('account:home')

    return redirect(flow.callback_uri)
