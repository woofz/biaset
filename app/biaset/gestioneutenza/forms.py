import random
from re import A
import string
from django import forms
from .models import Invito
from gestionecampionato.models import Campionato
from django.core.mail import send_mail
from datetime import datetime

class CreaInvitoForm(forms.ModelForm):
    
    class Meta:
        model = Invito
        fields = ('destinatario', 'expire_dt', 'user')
        widgets = {
            'destinatario': forms.EmailInput(attrs={'class': 'form-control'})
        }
        error_messages = {
            'data-non-valida': "L'invito deve avere una data di scadenza posteriore a quella odierna!"
        }
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Prendo il campionato dall'utente
        campionato = Campionato.objects.filter(championship_admin=instance.user).first()
        instance.campionato = campionato
        # Genero il codice invito
        codice_invito = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        instance.codice_invito = codice_invito
        self.send_email_notification(campionato, instance.destinatario, codice_invito)
        if commit:
            instance.save()
        return instance
    
    def send_email_notification(self, campionato: Campionato, destinatario: str, codice_invito: str) -> None:
        send_mail(
        "BiaSet - Invito iscrizione",
        f"Ciao! Sei stato invitato a partecipare al campionato {campionato.nome_campionato} da {campionato.championship_admin.first_name}. "  
        f"\nIl codice di invito è {codice_invito}. Visita il nostro sito (http://woofz.dev) per completare la registrazione. Per la registrazione, " \
        f"dovrai usare il social corrispondente a questo indirizzo e-mail." \
        f"\n \n Lo staff di BiaSet.",
        f'biaset@woofz.dev', 
        [destinatario],
        fail_silently=True)