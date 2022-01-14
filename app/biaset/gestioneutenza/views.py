from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.base import View
from django.contrib import messages
from .strategyclasses.strategy import Context, Strategy
from .strategyclasses.allenatorestrategy import AllenatoreStrategy
from .strategyclasses.castrategy import CaStrategy
from .strategyclasses.invitenotfound import InviteNotFoundException

class RegistrationView(View):
    template_name = "front/pages/gestioneutenza/registrazione.html"
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context={})
    

class StrategyRegistrationView(View):
    error_template_name = "front/error.html"
    strategy_context = Context(CaStrategy())

    def get(self, request, regtype: str):
        if regtype == 'allenatore':
            self.strategy_context = Context(AllenatoreStrategy())
        utente = User.objects.get(pk=request.user.pk)
        try:
            if self.strategy_context.doOperation(utente):
                messages.success(request, 'Registrazione avvenuta con successo!')
                return redirect(reverse('dashboard_index'))
        except InviteNotFoundException:
            error = 'Invito non valido o non esistente.'
        
        return render(request, self.error_template_name, context={'error': error})