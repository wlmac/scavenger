from django import forms

from .models import *


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
        exclude = (
            "id",
            "members",
            "is_active",
            "is_open",
            "completed_qr_codes",
            "current_qr_code",
        )


class TeamJoinForm(forms.Form):
    code = forms.CharField(
        label="Join Code",
        max_length=6,
        strip=True,
        required=True,
    )


class QrCodeAdminForm(forms.ModelForm):
    url = forms.CharField(disabled=True)

    class Meta:
        model = QrCode
        fields = "__all__"
