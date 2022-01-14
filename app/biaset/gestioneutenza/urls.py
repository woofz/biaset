from django.urls import path
from gestioneutenza.views import RegistrationView, StrategyRegistrationView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('registrazione/', login_required(RegistrationView.as_view()), name='registrazione'),
    path('registrazione/<str:regtype>/', login_required(StrategyRegistrationView.as_view()), name='registrazione_ca'),
]
