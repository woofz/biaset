from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import LoginView, HomeView

urlpatterns = [
    path('', login_required(HomeView.as_view()), name='dashboard_index'),
    path('login/', LoginView.as_view(), name='login_view'),
    path('gestioneutenza/', include(('gestioneutenza.urls', 'gestioneutenza'), namespace='gestioneutenza')),
]
