from django import forms
from django.utils.translation import gettext_lazy as _l

from .models import *


class TeamCreateForm(forms.ModelForm):
    class Meta:
        widgets = dict(
            name=forms.TextInput(attrs={"placeholder": "team name"}),
        )
        model = Team
        fields = ("name",)


class TeamJoinForm(forms.Form):
    code = forms.CharField(
        label=_l(""),
        max_length=8,
        strip=True,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "1a2b3c4d"}),
    )


class QrCodeAdminForm(forms.ModelForm):
    url = forms.CharField(disabled=True)

    class Meta:
        model = QrCode
        fields = "__all__"
