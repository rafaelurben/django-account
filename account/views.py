from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.mail import mail_admins

from .forms import ProfileForm, DeleteForm
from .utils import pop_session_next, account_entrypoint


# Create your views here.

@account_entrypoint()
def home(request):
    if not request.user.is_authenticated:
        return redirect(reverse("account:login"))
    return render(request, 'account/home.html')


def leave(request):
    nexturl = pop_session_next(request)
    return redirect(nexturl)


@account_entrypoint()
@login_required(login_url=reverse_lazy('account:home'))
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            nexturl = request.GET.get("next", "")
            if nexturl:
                return redirect(reverse('account:home') + "?next=" + nexturl)
            return redirect(reverse('account:home'))
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'account/profile.html', {'form': form})


@account_entrypoint()
@login_required(login_url=reverse_lazy('account:home'))
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
                    reverse("admin:auth_user_delete", args=(user.id,)))
            })

            mail_admins(subject, body)

            return render(request, 'account/account-delete-successful.html')
    else:
        form = DeleteForm()
    return render(request, 'account/account-delete.html', {'form': form})


def error404(request):
    return render(request, 'account/error.html', status=404)
