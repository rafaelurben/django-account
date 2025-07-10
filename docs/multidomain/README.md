# Multidomain Support

Multidomain support is useful when you have a single Django project that is reachable from multiple domains but you want
to limit the account management to a single domain.

Note that all domains **MUST share the same database**.

## Preparation

To use the multidomain support with a single django project, you need a way to set different url configs for different
domains.

For example, you might use a custom middleware that sets the `request.urlconf` attribute based on the request's host:

```python
# e. g. yourproject/middleware/virtualhost.py
from django.conf import settings


class VirtualHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        request.urlconf = getattr(settings, "VIRTUAL_HOSTS", {}).get(host, settings.ROOT_URLCONF)
        response = self.get_response(request)
        return response
```

Then, you can define your `VIRTUAL_HOSTS` in your `settings.py`:

```python
# e. g. yourproject/settings.py (excerpt)
MIDDLEWARE = [
    'yourproject.middleware.virtualhost.VirtualHostMiddleware',
    # ... other middleware ...
]

VIRTUAL_HOSTS = {
    "account.yourdomain.com": "yourproject.urls.account_urls",
    "app1.yourdomain.com": "yourproject.urls.app1_urls",
    "app2.yourotherdomain.com": "yourproject.urls.app2_urls",
}
```

You can also use a third-party package that provides similar functionality.

## Usage

In your account domain urlconfig, include `account.urls`, `account.multidomain.maindomain.urls` as well as urls for
social auth and passkeys:

```python
# e. g. yourproject/urls/account_urls.py
from django.urls import path, include

urlpatterns = [
    path('account/ext/', include('account.multidomain.maindomain.urls')),  # must come before 'account/'
    path('account/', include('account.urls')),  # required, basic account endpoints
    path('.well-known/', include('account.well_known.urls')),  # optional
    path('auth/', include('social_django.urls', namespace="social-auth")),  # for social auth
    path('passkeys/', include('passkeys.urls', namespace="passkeys")),  # for passkeys
    # ... other urls for your account domain ...
]
```

In your other (alternative) domain urlconfig, only include `account.multidomain.altdomain.urls`:

```python
# e. g. yourproject/urls/app1_urls.py and app2_urls.py
from django.urls import path, include

urlpatterns = [
    path('account/', include('account.multidomain.altdomain.urls')),
    # ... other urls for your alternative domain ...
]
```

> [!IMPORTANT]  
> Do NOT include `account.urls` in your alternative domain urlconfig!

Finally, in your settings, you must configure the `ACCOUNT_CONFIG.MULTIDOMAIN_MAINDOMAIN_EXT_ACCOUNT_BASE_URL` key to match the full base URL where you included `account.multidomain.maindomain.urls`:

```python
# e. g. yourproject/settings.py (excerpt)

ACCOUNT_CONFIG = {
    # ... other account config options ...
    'MULTIDOMAIN_MAINDOMAIN_EXT_ACCOUNT_BASE_URL': "https://account.yourdomain.com/account/ext/",
}
```

## How it works

The following diagrams show how the login and logout flows work:

- Login flow: [Login flow](./diagrams/login.puml)
- Logout flow: [Logout flow](./diagrams/logout.puml)

(You can view the diagrams by opening the `.puml` files in a PlantUML viewer or editor.)
