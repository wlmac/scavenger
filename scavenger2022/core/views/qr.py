import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.views import View
from ..models import QrCode, Hint


class QrView(View, LoginRequiredMixin):
    model = QrCode
    template_name = "core/qr.html"

    def get(self, request, id: int, *args, **kwargs):
        try:
            hint = random.choice(list(Hint.objects.filter(qr_code=id).values()))
        except Hint.DoesNotExist:
            return HttpResponseNotFound(
                "Hint's not found for that Qr code"
            )  # todo make look good
        print({"hint": hint["hint"]})
        return render(request, self.template_name, {"hint": hint["hint"]})
