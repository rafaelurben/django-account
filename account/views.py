from copy import deepcopy

from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.mail import mail_admins

from .forms import ProfileForm, DeleteForm
from .utils import pop_session_next, account_entrypoint, get_avatar_url


# Create your views here.

@account_entrypoint()
def home(request):
    if not request.user.is_authenticated:
        return redirect(reverse("account:login"))
    return render(request, 'account/home.html', {
        'avatar_url': get_avatar_url(request.user.email)
    })


def leave(request):
    nexturl = pop_session_next(request)
    return redirect(nexturl)


@account_entrypoint()
@login_required(login_url=reverse_lazy('account:login'))
def oauth_management(request):
    return render(request, 'account/oauth_management.html')


@account_entrypoint()
@login_required(login_url=reverse_lazy('account:login'))
def passkey_management(request):
    return redirect(reverse('passkeys:home'))


@account_entrypoint()
@login_required(login_url=reverse_lazy('account:login'))
def profile(request):
    # Copy needed because otherwise the template already receives new values even when an invalid form is submitted
    user = deepcopy(request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            nexturl = request.GET.get("next", "")
            if nexturl:
                return redirect(reverse('account:home') + "?next=" + nexturl)
            return redirect(reverse('account:home'))
    else:
        form = ProfileForm(instance=user)
    return render(request, 'account/profile.html', {'form': form})


@account_entrypoint()
@login_required(login_url=reverse_lazy('account:login'))
def delete_account(request):
    if request.method == "POST":
        form = DeleteForm(request.POST)
        if form.is_valid():
            user = request.user
            user.is_active = False
            user.save()
            logout(request)

            subject = f"Account disabled - please delete @{user.username}"
            body = get_template("account/account-delete-email.html").render({
                "user": user,
                "user_admin_url": request.build_absolute_uri(
                    reverse("admin:account_user_delete", args=(user.id,)))
            })

            mail_admins(subject, body)

            return render(request, 'account/account-delete-successful.html')
    else:
        form = DeleteForm()
    return render(request, 'account/account-delete.html', {'form': form})


def error404(request):
    return render(request, 'account/error.html', status=404)
