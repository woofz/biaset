from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import HomeView, ShowCaseView

urlpatterns = [
    path('', ShowCaseView.as_view(), name='index'),
    path('dashboard/', login_required(HomeView.as_view()), name='dashboard_index'),
    path('gestioneutenza/', include(('gestioneutenza.urls', 'gestioneutenza'), namespace='gestioneutenza')),
    path('gestionecampionato/', include(('gestionecampionato.urls', 'gestionecampionato'), namespace='gestionecampionato')),
    path('gestionesquadra/', include(('gestionesquadra.urls', 'gestionesquadra'), namespace='gestionesquadra')),
]
