from django import forms

from .models import Team


class TeamForm(forms.ModelForm):
    body = forms.CharField(
        required=True,
        widget=forms.widgets.Textarea(
            attrs={
                "placeholder": "test something...",
                "class": "textarea is-success is-medium",
            }
        ),
        label="",
    )

    class Meta:
        model = Team
        exclude = ("id", "members", "is_active", "is_open", "completed_qr_codes", "current_qr_code")
