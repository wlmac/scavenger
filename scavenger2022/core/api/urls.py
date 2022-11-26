from django.urls import include, path
from rest_framework.routers import SimpleRouter
from .views import *
from .views.codes import *

router = SimpleRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("qr/", code, name="code")
    ]
