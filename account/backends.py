"""
OAuth2 backend subclasses (from social-core)
"""

from requests import HTTPError

from social_core.exceptions import AuthCanceled
from social_core.backends import discord, google, github, azuread


# Note:
#
# The following subclasses are required to store the user's correct display name.
# Also, they check if the email is verified according to the API.
# If the email is not verified, the user is not allowed to login.


class DiscordOAuth2(discord.DiscordOAuth2):
    def extra_data(self, user, uid, response, details=None, *args, **kwargs):
        data = super().extra_data(user, uid, response, details, *args, **kwargs)

        username = response.get('username')
        discriminator = response.get('discriminator')
        if discriminator == "0":
            data['display_name'] = username
        else:
            data['display_name'] = f"{response.get('username')}#{response.get('discriminator')}"

        if not response.get('verified'):
            raise AuthCanceled(self, "Discord account email is not verified!")
        return data


class GoogleOAuth2(google.GoogleOAuth2):
    def extra_data(self, user, uid, response, details=None, *args, **kwargs):
        data = super().extra_data(user, uid, response, details, *args, **kwargs)
        data['display_name'] = response.get('email')

        if not response.get('email_verified'):
            raise AuthCanceled(self, "Google account email is not verified!")
        return data


class GithubOAuth2(github.GithubOAuth2):
    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        data = self._user_data(access_token)

        try:
            emails = self._user_data(access_token, '/emails')

            if emails:
                for email in emails:
                    if email.get('primary'):
                        data['email'] = email.get('email')
                        data['email_verified'] = email.get('verified')
                        break
        except (HTTPError, ValueError, TypeError):
            ...

        return data

    def extra_data(self, user, uid, response, details=None, *args, **kwargs):
        data = super().extra_data(user, uid, response, details, *args, **kwargs)
        data['display_name'] = response.get('login')

        if not response.get('email_verified', False):
            raise AuthCanceled(self, "GitHub account email is not verified!")
        return data


class MicrosoftOAuth2(azuread.AzureADOAuth2):
    """Default options already work well, no need to override"""
