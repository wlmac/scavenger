from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include('core.api.urls')),
    path('login/', views.oauth_login, name='oauth_login'),
    path('auth/', views.oauth_auth, name='oauth_auth'),
    path('logout/', views.logout, name='logout'),
]
