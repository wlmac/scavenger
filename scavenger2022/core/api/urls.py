from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views.codes import *

router = SimpleRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("qr/<int:id>", code, name="code"),
    path("codes/", codes, name="codes")

]
