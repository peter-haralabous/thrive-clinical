from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.decorators import login_not_required
from django.http import HttpRequest
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from sandwich.core.models.invitation import Invitation
from sandwich.core.models.invitation import InvitationStatus
from sandwich.core.service.invitation_service import accept_patient_invitation


class InvitationAcceptForm(forms.Form):
    accepted = forms.BooleanField(required=True, label="I accept the invitation")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))


@login_not_required
def accept_invite(request: HttpRequest, token: str) -> HttpResponse:
    invitation = get_object_or_404(
        Invitation.objects.filter(status=InvitationStatus.PENDING, expires_at__gt=timezone.now()), token=token
    )
    if not request.user.is_authenticated:
        return render(request, "patient/accept_invite_public.html", context={"invitation": invitation})

    if request.method == "POST":
        form = InvitationAcceptForm(request.POST)
        if form.is_valid():
            # TODO: if the user already has patients, they may want to merge one of them with the invited one
            accept_patient_invitation(invitation, request.user)
            return HttpResponseRedirect(
                reverse("patients:patient_details", kwargs={"patient_id": invitation.patient.id})
            )
    else:
        form = InvitationAcceptForm()

    context = {"invitation": invitation, "form": form}
    return render(request, "patient/accept_invite.html", context)
