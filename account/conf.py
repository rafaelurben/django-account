from django.conf import settings

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

