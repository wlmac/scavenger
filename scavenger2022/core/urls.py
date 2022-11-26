from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include('core.api.urls')),
    path('login/', views.login, name='login'),
    path('auth/', views.auth, name='auth'),
    path('logout/', views.logout, name='logout'),
]
