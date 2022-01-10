from django.shortcuts import render
from django.views import View
from django.core.mail import send_mail

class HomeView(View):
    '''Defines the dashboard home view'''
    template_name = "front/pages/dashboard-index.html"
    
    def get(self, request, *args, **kwargs):
       
        return render(request, self.template_name, context={})


class LoginView(View):
    '''Defines the login view'''
    template_name = "front/pages/login/login.html"
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context={})