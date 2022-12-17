from django import forms
from django.utils.translation import gettext_lazy as _l

from .models import *


class TeamMakeForm(forms.ModelForm):
    class Meta:
        widgets = dict(
            name=forms.TextInput(attrs={"placeholder": "youmas"}),
        )
        model = Team
        exclude = (
            "id",
            "members",
            "is_active",
            "is_open",
            "solo",
            "current_qr_i",
        )


class TeamJoinForm(forms.Form):
    code = forms.CharField(
        label=_l("join code"),
        max_length=8,
        strip=True,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "1a2b3c"}),
    )


class QrCodeAdminForm(forms.ModelForm):
    url = forms.CharField(disabled=True)

    class Meta:
        model = QrCode
        fields = "__all__"
