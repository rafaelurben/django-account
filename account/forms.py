from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.forms import fields, widgets
from django.utils.translation import gettext_lazy as _
from django.views.decorators.debug import sensitive_variables


class LoginForm(AuthenticationForm):
    passkeys = fields.CharField(required=False, widget=widgets.HiddenInput(attrs={"id": "passkeys"}))

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        self.fields["username"].required = False
        self.fields["username"].widget.attrs["autocomplete"] = "username webauthn"
        self.fields["password"].required = False

    @sensitive_variables()
    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        passkeys = self.cleaned_data.get("passkeys")

        if passkeys or (username is not None and password):
            if passkeys:  # If passkeys are provided, authenticate using them
                self.user_cache = authenticate(self.request)
            else:  # Otherwise, authenticate using username and password
                self.user_cache = authenticate(
                    self.request, username=username, password=password
                )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
        else:
            if not username:
                self.add_error("username", _("This field is required."))
            if not password:
                self.add_error("password", _("This field is required."))

        return self.cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]


class DeleteForm(forms.Form):
    confirm1 = forms.BooleanField(required=True,
                                  label=_("I really want to delete my account."))

    confirm2 = forms.BooleanField(required=True,
                                  label=_("I have read and understood the above notes."))

    confirm3 = forms.BooleanField(required=True,
                                  label=_("I am aware that all information linked to this account will be deleted."))
