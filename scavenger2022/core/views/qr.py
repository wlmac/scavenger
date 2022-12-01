import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.views.generic.detail import DetailView
from ..models import QrCode, Hint


class QrView(DetailView, LoginRequiredMixin):
    model = QrCode
    template_name = "core/qr.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hint"] = random.choice(list(self.object.hints.values()))
        # TODO: replace with ...filter(...).first() then if the user clicks new hint on qr.html get the 2nd hint and so on. note: use team_id as random seed for reproducibility
        return context
