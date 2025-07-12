"""Utils for the account app"""

import hashlib
from functools import wraps

NEXT_SESSION_KEY = "account_next"


def save_session_next(request, value=None):
    old_next = request.session.get(NEXT_SESSION_KEY, "")

    if value is not None:
        request.session[NEXT_SESSION_KEY] = value
    else:
        param = request.GET.get("next", "")
        if param != "":
            request.session[NEXT_SESSION_KEY] = request.GET.get("next").split("://")[-1]
        elif old_next == "":
            request.session[NEXT_SESSION_KEY] = "/"


def pop_session_next(request, default="/"):
    return request.session.pop(NEXT_SESSION_KEY, default)


def account_entrypoint():
    """Decorator for views

    Saves the next param (if available) to the session"""

    def decorator(function):
        @wraps(function)
        def wrap(request, *args, **kwargs):
            save_session_next(request)

            return function(request, *args, **kwargs)

        return wrap

    return decorator


def get_avatar_url(email, size="300") -> str:
    """
    Generate the avatar url for this user for the gravatar service.
    The email address itself is never passed to the service.
    More info: https://gravatar.com/site/implement/images/
    """
    mailhash = hashlib.md5(str(email).encode("utf-8")).hexdigest()
    return f"https://www.gravatar.com/avatar/{mailhash}?s={size}&d=retro"
