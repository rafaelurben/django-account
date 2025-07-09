from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

SETTINGS_KEY = 'ACCOUNT_CONFIG'


class Config:
    APPLICATION_HEADER = _('Account management')
    APPLICATION_NAME = _('this webapp')

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
    }

    HELP_SUPPORT_OPTIONS: list[tuple[str]] | None = None

    _OPTIONAL_SETTINGS = ['APPLICATION_HEADER', 'APPLICATION_NAME', 'HELP_SUPPORT_OPTIONS']
    _EXTENDABLE_DICT_SETTINGS = ['BACKENDS_DISPLAY_CONFIG']

    def __init__(self):
        user_settings: dict | None = getattr(settings, SETTINGS_KEY, None)

        if user_settings is None:
            return
        if not isinstance(user_settings, dict):
            raise ImproperlyConfigured(f"The settings key {SETTINGS_KEY} must be a dictionary, if present.")

        for key in self._OPTIONAL_SETTINGS:
            if key in user_settings:
                setattr(self, key, user_settings[key])
        for key in self._EXTENDABLE_DICT_SETTINGS:
            if key in user_settings:
                if not isinstance(user_settings[key], dict):
                    raise ImproperlyConfigured(f"The key '{key}' must be a dictionary.")
                getattr(self, key).update(user_settings[key])

        # Check for redundant settings
        for key in user_settings:
            if key not in self._OPTIONAL_SETTINGS and key not in self._EXTENDABLE_DICT_SETTINGS:
                raise ImproperlyConfigured(f"The key '{key}' is not a valid setting for {SETTINGS_KEY}.")


config = Config()
