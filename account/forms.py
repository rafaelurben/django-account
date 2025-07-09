from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.forms import fields, widgets


class LoginForm(AuthenticationForm):
    passkeys = fields.CharField(required=False, widget=widgets.HiddenInput(attrs={"id": "passkeys"}))

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        self.fields["username"].required = False
        self.fields["username"].widget.attrs["autocomplete"] = "username webauthn"
        self.fields["password"].required = False

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        passkeys = self.cleaned_data.get("passkeys")

        if passkeys or (username is not None and password):
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
        else:
            if not username:
                self.add_error("username", "Dieses Feld ist zwingend erforderlich.")
            if not password:
                self.add_error("password", "Dieses Feld ist zwingend erforderlich.")

        return self.cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]


class DeleteForm(forms.Form):
    confirm1 = forms.BooleanField(required=True,
                                  label="Ich möchte meinen Account wirklich löschen.")

    confirm2 = forms.BooleanField(required=True,
                                  label="Ich habe obige Hinweise gelesen und verstanden.")

    confirm3 = forms.BooleanField(required=True,
                                  label="Ich bin mir bewusst, dass sämtliche mit diesem Account verknüpfte "
                                        "Informationen gelöscht werden.")
