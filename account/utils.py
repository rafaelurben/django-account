"""Utils for the account app"""

import hashlib
from functools import wraps


def save_session_next(request):
    session = request.session.get("account_next", "")
    param = request.GET.get("next", "")
    if param != "":
        request.session['account_next'] = request.GET.get("next").split("://")[-1]
    elif session == "":
        request.session['account_next'] = "/"


def pop_session_next(request, default="/"):
    return request.session.pop("account_next", default)


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
