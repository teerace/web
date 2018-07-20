from django.http import HttpResponseRedirect


class BetaMiddleware:
    """
    Require beta code cookie key in order to view any page.
    """

    def process_request(self, request):
        if request.path[:6] in (
            "/beta/",
            "/login",
            "/media",
            "/api/1",
            "/blog/",
            "/about",
        ):
            return
        if (
            request.method == "GET"
            and not request.user.is_authenticated
            and not "is_in_beta" in request.session
        ):
            return HttpResponseRedirect("/beta/?next=%s" % request.path)
