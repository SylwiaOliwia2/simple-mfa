from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('mfa/verify/', views.verify_mfa, name='verify_mfa'),
    path('mfa/setup/', views.mfa_setup, name='mfa_setup'),
    path('mfa/confirm/', views.mfa_confirm, name='mfa_confirm'),
    path('welcome/', views.welcome, name='welcome'),
    path('lucky-number/', views.lucky_number, name='lucky_number'),
    path('quote-of-the-day/', views.quote_of_the_day, name='quote_of_the_day'),
    path('notes/', views.notes_list, name='notes_list'),
    path('notes/create/', views.notes_create, name='notes_create'),
    path('notes/<int:note_id>/download/', views.notes_download, name='notes_download'),
    path('notes/<int:note_id>/delete/', views.notes_delete, name='notes_delete'),
]
