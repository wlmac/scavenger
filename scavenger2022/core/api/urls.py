from django.urls import include, path

from .views.codes import *


urlpatterns = [
    path("qr/<int:id>", code, name="code"),
    path("codes/", codes, name="codes"),
]
