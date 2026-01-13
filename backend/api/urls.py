from django.urls import path
from . import views

urlpatterns = [
    path('csrf-token/', views.csrf_token, name='csrf_token'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('mfa/verify/', views.verify_mfa, name='verify_mfa'),
    path('mfa/setup/', views.mfa_setup, name='mfa_setup'),
    path('mfa/confirm/', views.mfa_confirm, name='mfa_confirm'),
    path('welcome/', views.welcome, name='welcome'),
]
