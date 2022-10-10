# Django accounts

A simple django app used in <https://app.rafaelurben.ch/account> to manage user accounts. Not meant to be used elsewhere without further modifications.

Depends on [social-auth-app-django](https://github.com/python-social-auth/social-app-django).

## Features

- [x] Account overview page
- [x] OAuth2 login and registration via
  - [x] Google
  - [x] Discord
  - [x] GitHub
- [x] Login via username and password
- [x] Password change / reset
- [x] Logout
- [x] "Back to app" button
- [x] Help section

### Planned features

- [ ] Register via email

## Example settings

settings.py (excerpt)

```python
SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_LOGIN_ERROR_URL = reverse_lazy('account:home')

SOCIAL_AUTH_URL_NAMESPACE = 'social-auth'

SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. In some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social_core.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social_core.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    'social_core.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social_core.pipeline.social_auth.social_user',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'social_core.pipeline.user.get_username',

    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    # 'social_core.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    'social_core.pipeline.social_auth.associate_by_email',

    # Create a user account if we haven't found one yet.
    'social_core.pipeline.user.create_user',

    # Create the record that associates the social account with the user.
    'social_core.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social_core.pipeline.social_auth.load_extra_data',

    # Update the user record with any changed info from the auth service.
    'social_core.pipeline.user.user_details',
)

AUTHENTICATION_BACKENDS = (
    'account.backends.GithubOAuth2',
    'account.backends.GoogleOAuth2',
    'account.backends.DiscordOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# OAuth Google config

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv("OAUTH_GOOGLE_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv("OAUTH_GOOGLE_SECRET")

SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
    'prompt': 'select_account'
}

# OAuth GitHub config

SOCIAL_AUTH_GITHUB_KEY = os.getenv("OAUTH_GITHUB_KEY")
SOCIAL_AUTH_GITHUB_SECRET = os.getenv("OAUTH_GITHUB_SECRET")

SOCIAL_AUTH_GITHUB_SCOPE = ["user:email"]

# OAuth Discord config

SOCIAL_AUTH_DISCORD_KEY = os.getenv("OAUTH_DISCORD_KEY")
SOCIAL_AUTH_DISCORD_SECRET = os.getenv("OAUTH_DISCORD_SECRET")

SOCIAL_AUTH_DISCORD_SCOPE = ["identify", "email"]
```
