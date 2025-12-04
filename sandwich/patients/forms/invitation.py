from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from sandwich.core.models import Invitation


class InvitationAcceptForm(forms.Form):
    accepted = forms.BooleanField(required=True, label="I accept the invitation")

    def __init__(self, *args, invitation: Invitation, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._invitation = invitation
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))


class DateOfBirthInvitationAcceptForm(InvitationAcceptForm):
    date_of_birth = forms.DateField(
        required=True, label="Date of birth", widget=forms.DateInput(attrs={"type": "date"})
    )

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data["date_of_birth"]
        if date_of_birth != self._invitation.patient.date_of_birth:
            self._invitation.increment_verification_attempts()
            raise forms.ValidationError("Incorrect date of birth.")
        return date_of_birth
