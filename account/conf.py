from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Config:
    APPLICATION_HEADER = getattr(settings, 'ACCOUNT_APPLICATION_HEADER', _('Account management'))
    APPLICATION_NAME = getattr(settings, 'ACCOUNT_APPLICATION_NAME', _('this webapp'))

    BACKENDS_DISPLAY_CONFIG = {
        'google-oauth2': {
            'title': 'Google',
            'icon': 'account/icons/logo_google-oauth2.svg',
        },
        'github': {
            'title': 'GitHub',
            'icon': 'account/icons/logo_github.svg',
        },
        'discord': {
            'title': 'Discord',
            'icon': 'account/icons/logo_discord.svg',
        },
        'azuread-oauth2': {
            'title': 'Microsoft',
            'icon': 'account/icons/logo_azuread-oauth2.svg',
        },
        **getattr(settings, 'ACCOUNT_BACKENDS_DISPLAY_CONFIG', dict()),
    }

    HELP_SUPPORT_OPTIONS: list[tuple[str]] = getattr(settings, 'ACCOUNT_HELP_SUPPORT_OPTIONS', None)
