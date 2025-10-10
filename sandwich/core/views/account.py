import logging

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.forms import AccountDeleteForm
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@login_required
def account_delete(request: AuthenticatedHttpRequest) -> HttpResponse:
    logger.info("Accessing account delete", extra={"user_id": request.user.id})

    if request.method == "POST":
        logger.info("Processing account delete form", extra={"user_id": request.user.id})
        form = AccountDeleteForm(request.POST)
        if not form.is_valid():
            return render(request, "users/account_delete.html", context={"form": form})

        user = request.user
        logout(request)
        user.delete_account()
        logger.info("Account deleted successfully", extra={"user_id": user.id})
        # TODO: send them to a "we're sorry to see you go" page instead?
        return redirect(reverse("account_login"))

    logger.debug("Rendering account delete form", extra={"user_id": request.user.id})
    form = AccountDeleteForm()

    context = {"form": form}
    return render(request, "users/account_delete.html", context)
