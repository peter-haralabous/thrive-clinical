from crispy_forms.helper import FormHelper
from django import forms
from django.db.models import QuerySet
from guardian.shortcuts import get_objects_for_user

from sandwich.core.inputs import RoundIconButton
from sandwich.core.models import Patient
from sandwich.users.models import User


class ChatForm(forms.Form):
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.none(),  # Queryset populated in __init__
        required=True,
        widget=forms.HiddenInput,
    )
    message = forms.CharField(
        required=True, widget=forms.Textarea(attrs={"placeholder": "Ask a question or add notes..."})
    )
    thread = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, user: User, **kwargs):
        self._user = user
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.add_input(
            RoundIconButton(
                icon="arrow-up",
            )
        )
        self.fields["patient"].queryset = self._patient_queryset()  # type: ignore[attr-defined]

    def _patient_queryset(self) -> QuerySet[Patient]:
        return get_objects_for_user(self._user, "view_patient", Patient)
