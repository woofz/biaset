from django import forms

from gestionecampionato.models import Campionato

class CreaCampionatoForm(forms.ModelForm):
    
    class Meta:
        model = Campionato
        fields = ('nome_campionato', 'max_partecipanti', 'championship_admin')
        widgets = {
            'nome_campionato': forms.TextInput(attrs={'class': 'form-control'}),
            'max_partecipanti': forms.TextInput(attrs={'class': 'form-control'})
        }


class ModificaCampionatoForm(forms.ModelForm):
    
    class Meta:
        model = Campionato
        fields = ('nome_campionato',)
        widgets = {
            'nome_campionato': forms.TextInput(attrs={'class': 'form-control'}),
        }