from django.utils.translation import ugettext_lazy as _
from rest_framework import HTTP_HEADER_ENCODING, exceptions
from rest_framework.authentication import BaseAuthentication

from race.models import Server


def get_authorization_header(request):
    auth = request.META.get("HTTP_API_AUTH", b"")
    if isinstance(auth, str):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


def get_server_from_key(key):
    try:
        server = Server.objects.select_related("maintained_by").get(api_key=key)
    except Server.DoesNotExist:
        raise exceptions.AuthenticationFailed(_("Invalid token."))

    if not server.is_active:
        raise exceptions.AuthenticationFailed(_("Server inactive or deleted."))

    return (server.maintained_by, server)


class ServerTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request)

        if not auth:
            return None

        try:
            token = auth.decode()
        except UnicodeError:
            msg = _(
                "Invalid token header. Token string should not contain invalid characters."
            )
            raise exceptions.AuthenticationFailed(msg)

        return get_server_from_key(token)
