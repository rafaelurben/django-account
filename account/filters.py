import passkeys.models as passkey_models
import social_django.models as socialauth_models
from django.contrib.admin import SimpleListFilter
from django.db.models import Q, Value, BooleanField, Case, When, Exists, OuterRef
from django.utils.translation import gettext as _


class HasUsablePasswordFilter(SimpleListFilter):
    title = _("password?")
    parameter_name = "has_usable_password"

    def lookups(self, request, model_admin):
        return ("1", _("Yes")), ("0", _("No"))

    def queryset(self, request, queryset):
        value = self.value()
        if value in {"0", "1"}:
            queryset = queryset.annotate(
                has_usable_password=Case(
                    When(
                        Q(password__isnull=False) & ~Q(password__startswith="!"), then=Value(True)
                    ),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
            return queryset.filter(has_usable_password=(value == "1"))
        return queryset


class HasUsablePasskeyFilter(SimpleListFilter):
    title = _("passkey?")
    parameter_name = "has_usable_passkey"

    def lookups(self, request, model_admin):
        return ("1", _("Yes")), ("0", _("No"))

    def queryset(self, request, queryset):
        value = self.value()
        if value in {"0", "1"}:
            queryset = queryset.annotate(
                has_usable_passkey=Exists(
                    passkey_models.UserPasskey.objects.filter(user=OuterRef("pk"), enabled=True)
                )
            )
            return queryset.filter(has_usable_passkey=(value == "1"))
        return queryset


class HasUsableOAuthFilter(SimpleListFilter):
    title = _("OAuth?")
    parameter_name = "has_usable_oauth"

    def lookups(self, request, model_admin):
        return ("1", _("Yes")), ("0", _("No"))

    def queryset(self, request, queryset):
        value = self.value()
        if value in {"0", "1"}:
            queryset = queryset.annotate(
                has_usable_oauth=Exists(
                    socialauth_models.UserSocialAuth.objects.filter(user=OuterRef("pk"))
                )
            )
            return queryset.filter(has_usable_oauth=(value == "1"))
        return queryset
