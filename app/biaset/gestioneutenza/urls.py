from django.urls import path
from gestioneutenza.views import RegistrationView, StrategyRegistrationView, LoginView, InviteCreateView, LogoutView, ListUtentiView
from django.contrib.auth.decorators import login_required

app_name = 'gestioneutenza'
urlpatterns = [
    path('registrazione/', login_required(RegistrationView.as_view()), name='registrazione'),
    path('registrazione/<str:regtype>/', login_required(StrategyRegistrationView.as_view()), name='registrazione_ca'),
    path('login/', LoginView.as_view(), name='login_view'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('creainvito/', InviteCreateView.as_view(), name='crea_invito'),
    path('utenti/', login_required(ListUtentiView.as_view()), name='list_utenti')
]
