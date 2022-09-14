"Account middleware"

from social_django.middleware import SocialAuthExceptionMiddleware
from social_core import exceptions as social_exceptions
from django.http import HttpResponse


class AuthExceptionMiddleware(SocialAuthExceptionMiddleware):

    def raise_exception(self, request, exception):
        return False
