from django import forms

from .models import *


class TeamMakeForm(forms.ModelForm):
    class Meta:
        model = Team
        exclude = (
            "id",
            "members",
            "is_active",
            "is_open",
            "completed_qr_codes",
            "current_qr_code",
            "solo",
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
