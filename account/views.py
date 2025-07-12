from copy import deepcopy

from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.core.mail import mail_admins
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext as _

from .forms import ProfileForm, DeleteForm
from .utils import pop_session_next, account_entrypoint, get_avatar_url


# Create your views here.


@account_entrypoint()
def home(request):
    if not request.user.is_authenticated:
        return redirect(reverse("account:login"))
    return render(
        request,
        "account/home.html",
        {
            "avatar_url": get_avatar_url(request.user.email),
            "has_usable_password": request.user.has_usable_password(),
            "has_usable_passkey": request.user.userpasskey_set.filter(enabled=True).count() > 0,
            "has_usable_oauth": request.user.social_auth.count() > 0,
        },
    )


def leave(request):
    nexturl = pop_session_next(request)
    return redirect(nexturl)


class LogoutView(auth_views.LogoutView):
    http_method_names = ["get", "post", "options"]

    def post(self, request, *args, **kwargs):
        messages.success(request, _("You are now logged out!"))
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


@account_entrypoint()
@login_required(login_url=reverse_lazy("account:login"))
def oauth_management(request):
    return render(request, "account/oauth_management.html")


@account_entrypoint()
@login_required(login_url=reverse_lazy("account:login"))
def passkey_management(request):
    return redirect(reverse("passkeys:home"))


@account_entrypoint()
@login_required(login_url=reverse_lazy("account:login"))
def profile(request):
    # Copy needed because otherwise the template already receives new values even when an invalid form is submitted
    user = deepcopy(request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            nexturl = request.GET.get("next", "")
            if nexturl:
                return redirect(reverse("account:home") + "?next=" + nexturl)
            return redirect(reverse("account:home"))
    else:
        form = ProfileForm(instance=user)
    return render(request, "account/profile.html", {"form": form})


@account_entrypoint()
@login_required(login_url=reverse_lazy("account:login"))
def delete_account(request):
    if request.method == "POST":
        form = DeleteForm(request.POST)
        if form.is_valid():
            user = request.user
            user.is_active = False
            user.save()
            auth_logout(request)

            subject = f"Account disabled - please delete @{user.username}"
            body = get_template("account/account-delete-email.html").render(
                {
                    "user": user,
                    "user_admin_url": request.build_absolute_uri(
                        reverse("admin:account_user_delete", args=(user.id,))
                    ),
                }
            )

            mail_admins(subject, body)

            return render(request, "account/account-delete-successful.html")
    else:
        form = DeleteForm()
    return render(request, "account/account-delete.html", {"form": form})


@account_entrypoint()
@login_required(login_url=reverse_lazy("account:login"))
def delete_password(request):
    if not request.user.has_usable_password():
        messages.error(
            request, _("You do not currently have a usable password set that could be deleted.")
        )
        return redirect(reverse("account:home"))

    if not (
        request.user.userpasskey_set.filter(enabled=True).count() > 0
        or request.user.social_auth.count() > 0
    ):
        messages.error(
            request,
            _(
                "You must have at least one usable passkey or OAuth account to delete your password."
            ),
        )
        return redirect(reverse("account:home"))

    if request.method == "POST":
        user = request.user
        user.set_unusable_password()
        user.save()

        messages.success(
            request,
            _(
                "Your password has been successfully deleted. Please sign back in using another method."
            ),
        )
        return redirect(reverse("account:home"))
    return render(request, "account/password-delete.html")


def error404(request):
    return render(request, "account/error.html", status=404)
