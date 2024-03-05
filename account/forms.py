from django import forms
from django.contrib.auth.models import User


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
