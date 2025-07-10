"""Account middleware"""

from social_django.middleware import SocialAuthExceptionMiddleware


class AuthExceptionMiddleware(SocialAuthExceptionMiddleware):

    def raise_exception(self, request, exception):
        return False
