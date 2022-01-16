from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.base import View
from django.contrib import messages
from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from .models import Invito
from .forms import CreaInvitoForm
from .strategyclasses.strategy import Context, Strategy
from .strategyclasses.allenatorestrategy import AllenatoreStrategy
from .strategyclasses.castrategy import CaStrategy
from .strategyclasses.invitenotfound import InviteNotFoundException
from django.contrib.auth import logout
from core.decorators import check_if_profile_exists, check_user_permission_ca
from django.utils.decorators import method_decorator

decorators_ca = [check_user_permission_ca]

class RegistrationView(View):
    template_name = "front/pages/gestioneutenza/registrazione.html"
    
    @method_decorator(check_if_profile_exists)
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context={})
    

class StrategyRegistrationView(View):
    error_template_name = "front/error.html"
    strategy_context = Context(CaStrategy())

    @method_decorator(check_if_profile_exists)
    def get(self, request, regtype: str):
        error = 'Invito non valido o non esistente.'
        if regtype == 'allenatore':
            self.strategy_context = Context(AllenatoreStrategy())
        utente = User.objects.get(pk=request.user.pk)
        try:
            if self.strategy_context.doOperation(utente):
                messages.success(request, 'Registrazione avvenuta con successo!')
                return redirect(reverse('dashboard_index'))
        except InviteNotFoundException:
            pass
        
        return render(request, self.error_template_name, context={'error': error})
    

class LoginView(View):
    '''Definisce la login view'''
    template_name = "front/pages/gestioneutenza/login.html"
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context={})
    

class LogoutView(View):
    
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('dashboard_index'))


@method_decorator(decorators_ca, name='dispatch')
class InviteCreateView(SuccessMessageMixin, CreateView):
    model = Invito
    template_name = "front/pages/gestioneutenza/creainvito.html"
    form_class = CreaInvitoForm
    success_url = reverse_lazy('dashboard_index')
    success_message = 'Invito creato correttamente!'