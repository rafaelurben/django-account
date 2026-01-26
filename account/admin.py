import passkeys.models as passkey_models
import social_django.models as socialauth_models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import OuterRef, Exists, Case, When, Q, Value, BooleanField
from django.utils.translation import gettext as _

from account.filters import HasUsablePasswordFilter, HasUsablePasskeyFilter, HasUsableOAuthFilter
from account.models import User

# We're adding a custom admin that extends the default user admin


class UserAdminPasskeyInline(admin.TabularInline):
    model = passkey_models.UserPasskey
    extra = 0
    verbose_name = _("passkey")
    verbose_name_plural = _("passkeys")
    fields = ("name", "enabled", "platform", "credential_id", "added_on", "last_used")
    readonly_fields = ("added_on", "last_used", "credential_id", "token")

    def has_add_permission(self, request, obj):
        return False


class UserAdminSocialAuthInline(admin.TabularInline):
    model = socialauth_models.UserSocialAuth
    extra = 0
    verbose_name = _("third-party account")
    verbose_name_plural = _("third-party accounts")
    fields = ("provider", "uid", "extra_data", "created", "modified")
    readonly_fields = ("provider", "uid", "created", "modified")

    def has_add_permission(self, request, obj):
        return False


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "has_usable_password",
        "has_usable_passkey",
        "has_usable_oauth",
        "date_joined",
        "last_login",
    )
    list_filter = (
        "is_staff",
        "is_active",
        "is_superuser",
        "date_joined",
        "last_login",
        HasUsablePasswordFilter,
        HasUsablePasskeyFilter,
        HasUsableOAuthFilter,
    )

    inlines = (UserAdminPasskeyInline, UserAdminSocialAuthInline)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                annotation_has_usable_password=Case(
                    When(
                        Q(password__isnull=False) & ~Q(password__startswith="!"), then=Value(True)
                    ),
                    default=Value(False),
                    output_field=BooleanField(),
                ),
                annotation_has_usable_passkey=Exists(
                    passkey_models.UserPasskey.objects.filter(user=OuterRef("pk"), enabled=True)
                ),
                annotation_has_usable_oauth=Exists(
                    socialauth_models.UserSocialAuth.objects.filter(user=OuterRef("pk"))
                ),
            )
        )

    # Admin displays

    @admin.display(
        boolean=True, description=_("password?"), ordering="annotation_has_usable_password"
    )
    def has_usable_password(self, user):
        return user.annotation_has_usable_password

    @admin.display(
        boolean=True, description=_("passkey?"), ordering="annotation_has_usable_passkey"
    )
    def has_usable_passkey(self, user):
        return user.annotation_has_usable_passkey

    @admin.display(boolean=True, description=_("OAuth?"), ordering="annotation_has_usable_oauth")
    def has_usable_oauth(self, user):
        return user.annotation_has_usable_oauth
