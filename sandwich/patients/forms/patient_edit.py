from datetime import date

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from django import forms
from django.urls import reverse

from sandwich.core.models import Patient
from sandwich.core.validators.date_of_birth import valid_date_of_birth
from sandwich.core.validators.phn import clean_phn


class PatientEdit(forms.ModelForm[Patient]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["province"].widget.attrs.update(
            {
                "hx-get": reverse("patients:get_phn_validation"),
                "hx-target": "#div_id_phn",
                "hx-trigger": "change",
            }
        )
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div("first_name", "last_name", css_class="flex gap-4"),
            "date_of_birth",
            "province",
            "phn",
            Submit("submit", "Submit"),
        )

    def clean_date_of_birth(self) -> date:
        dob = self.cleaned_data["date_of_birth"]
        return valid_date_of_birth(dob)

    def clean_phn(self):
        """Custom validation for the BC PHN field."""
        province = self.cleaned_data.get("province")
        phn = str(self.cleaned_data.get("phn"))
        if not province or not phn:
            return phn
        cleaned_phn = clean_phn(province, phn)
        if cleaned_phn is not None:
            return cleaned_phn
        error_message = "Invalid phn"
        raise forms.ValidationError(error_message)

    class Meta:
        model = Patient
        fields = ("first_name", "last_name", "date_of_birth", "province", "phn")

        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date", "max": "9999-12-31"}),
        }
