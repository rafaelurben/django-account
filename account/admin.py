import passkeys.models as passkey_models
import social_django.models as socialauth_models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User as DjangoUser


# Proxy models

class User(DjangoUser):
    class Meta(DjangoUser.Meta):
        proxy = True


# We're adding a custom admin that extends the default user admin

class UserAdminPasskeyInline(admin.TabularInline):
    model = passkey_models.UserPasskey
    extra = 0
    verbose_name = 'Passkey'
    verbose_name_plural = 'Passkeys'
    fields = ('name', 'enabled', 'platform', 'credential_id', 'added_on', 'last_used')
    readonly_fields = ('added_on', 'last_used', 'credential_id', 'token')

    def has_add_permission(self, request, obj):
        return False


class UserAdminSocialAuthInline(admin.TabularInline):
    model = socialauth_models.UserSocialAuth
    extra = 0
    verbose_name = 'Drittanbieter-Account'
    verbose_name_plural = 'Drittanbieter-Accounts'
    fields = ('provider', 'uid', 'extra_data', 'created', 'modified')
    readonly_fields = ('provider', 'uid', 'created', 'modified')

    def has_add_permission(self, request, obj):
        return False


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'has_usable_password', 'has_usable_passkey', 'has_usable_oauth')

    inlines = (UserAdminPasskeyInline, UserAdminSocialAuthInline)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('social_auth', 'userpasskey_set')

    # Admin displays

    @admin.display(boolean=True, description='Passwort?')
    def has_usable_password(self, user: DjangoUser):
        return user.has_usable_password()

    @admin.display(boolean=True, description='Passkey?')
    def has_usable_passkey(self, user: DjangoUser):
        return user.userpasskey_set.filter(enabled=True).count() > 0

    @admin.display(boolean=True, description='OAuth?')
    def has_usable_oauth(self, user: DjangoUser):
        return user.social_auth.count() > 0
