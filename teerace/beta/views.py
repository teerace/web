from annoying.decorators import render_to
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect

from accounts.forms import LoginForm
from beta.forms import BetaForm, MoarKeysForm
from blog.services import latest_entries


@render_to("beta/beta_form.html")
def beta_form(request):
    if request.user.is_authenticated:
        return redirect(reverse("home"))

    form = BetaForm(request=request)
    login_form = LoginForm()

    if request.method == "POST":
        form = BetaForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Welcome. You are now allowed to register"
                " an account. Please report all encountered errors and issues.",
            )
            messages.warning(
                request,
                "By the way, it is recommended that you"
                " register an account now, because you won't be able to reuse"
                " your beta key!",
            )
            return redirect(reverse("register"))

    _request = None
    if request.method == "POST":
        _request = request.POST.copy()
    else:
        _request = request.GET.copy()

    return {
        "form": form,
        "latest_entries": latest_entries(),
        "login_form": login_form,
        "next": _request.get("next", reverse("home")),
    }


@render_to("beta/moar_keys.html")
def moar_keys(request):
    user = request.user
    if not user.is_staff and not user.is_superuser:
        messages.error(request, "Nope, you cannot do that.")
        return redirect(reverse("home"))

    new_keys = None

    form = MoarKeysForm()
    if request.method == "POST":
        form = MoarKeysForm(request.POST)
        if form.is_valid():
            form.save()
            new_keys = form.new_keys
            messages.success(request, "Created %d new key(s)!" % len(new_keys))

    return {"form": form, "new_keys": new_keys}
