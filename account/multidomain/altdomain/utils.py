from django.contrib.auth import login, get_backends
from django.utils.translation import gettext as _

from account.multidomain.exceptions import AuthFlowException


def login_with_any_backend(request, user):
    """Attempt to log in a user with any available authentication backend."""

    for backend in get_backends():
        if hasattr(backend, 'get_user'):
            try:
                if backend.get_user(user.pk) == user:
                    login(request, user, backend=backend.__module__ + '.' + backend.__class__.__name__)
                    return
            except Exception:
                continue
    raise AuthFlowException(_("No compatible authentication backend found for signing in. Please contact support."))
