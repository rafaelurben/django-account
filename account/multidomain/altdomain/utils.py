import logging

from django.contrib.auth import login, get_backends
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext as _

from account.multidomain.exceptions import AuthFlowException

logger = logging.getLogger(__name__)


def login_with_any_backend(request, user):
    """Attempt to log in a user with any available authentication backend."""

    for backend in get_backends():
        if hasattr(backend, "get_user"):
            try:
                if backend.get_user(user.pk) == user:
                    backend_name = backend.__module__ + "." + backend.__class__.__name__
                    login(request, user, backend=backend_name)
                    logger.info("User %s logged in using backend: %s", user, backend_name)
                    return
            except (
                user.__class__.DoesNotExist,
                AttributeError,
                TypeError,
                ValueError,
                ImproperlyConfigured,
            ):
                logger.warning(
                    "Backend %s failed to authenticate user %s: %s", backend, user, exc_info=True
                )
                continue
    raise AuthFlowException(
        _("No compatible authentication backend found for signing in. Please contact support.")
    )
