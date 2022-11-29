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
            qr = QrCode.objects.get(id=id)
        except QrCode.DoesNotExist:
            return HttpResponseNotFound("QR code not found")
        qr_data = {"id": qr.id, "location": qr.location}
        hint = random.choice(list(Hint.objects.filter(qr_code=qr.id).values()))
        del hint["qr_code_id"], hint["id"]

        return render(request, self.template_name, {"qr": qr_data, "hint": hint})
