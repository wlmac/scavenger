from django.urls import path, include
from . import views

urlpatterns = [
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('', views.index, name='index'),
]
