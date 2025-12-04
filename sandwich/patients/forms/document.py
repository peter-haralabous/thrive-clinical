from django import forms

from sandwich.core.models import Document
from sandwich.core.service.ingest_service import ProcessDocumentContext

SUPPORTED_FILE_TYPES = ["application/pdf", "text/plain"]


class DocumentForm(forms.ModelForm):
    context = forms.ChoiceField(widget=forms.HiddenInput, required=False, choices=ProcessDocumentContext.choices)

    class Meta:
        model = Document
        fields = ("file", "patient", "encounter")

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if getattr(file, "content_type", None) not in SUPPORTED_FILE_TYPES:
            msg = "Unsupported file type."
            raise forms.ValidationError(msg)
        return file

    def save(self, commit=True):  # noqa: FBT002
        instance = super().save(commit=False)
        file = self.cleaned_data.get("file")
        if file:
            instance.content_type = getattr(file, "content_type", "")
            instance.size = getattr(file, "size", None)
            instance.original_filename = getattr(file, "name", "")
        if commit:
            instance.save()
        return instance
