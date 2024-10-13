from django import template
import account.conf as conf

register = template.Library()


@register.simple_tag(name="backend_display_config")
def get_backend_display_config(backend):
    return conf.BACKENDS_DISPLAY_CONFIG.get(backend, dict())
