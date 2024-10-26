from django import template
from account.conf import Config

register = template.Library()


@register.simple_tag(name="backend_display_config")
def get_backend_display_config(backend):
    return Config.BACKENDS_DISPLAY_CONFIG.get(backend, dict())


@register.simple_tag(name="account_config")
def get_account_config(option):
    return getattr(Config, option, None)
