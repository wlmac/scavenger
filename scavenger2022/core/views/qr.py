import random
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
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


@login_required
@require_http_methods(("GET", "POST"))
def qr(request, key):
    context = dict(first=False)
    context["qr"] = qr = get_object_or_404(QrCode, key=key)
    i = (codes := QrCode.code_pks(request.user)).index(qr.id) + 1
    context["nextqr"] = None if len(codes) <= i else QrCode.objects.get(id=codes[i])
    return render(request, "core/qr.html", context=context)


@login_required
@require_http_methods(("GET", "POST"))
def qr_first(request):
    context = dict(first=True)
    context["qr"] = qr = QrCode.codes(request.user)[0]
    i = (codes := QrCode.code_pks(request.user)).index(qr.id) + 1
    context["nextqr"] = None if len(codes) <= i else QrCode.objects.get(id=codes[i])
    return render(request, "core/qr.html", context=context)
