from random import choice
from django.core.exceptions import ValidationError
from django import forms
from gestionesquadra.models import Giocatore, Squadra

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


class SelezionaModuloForm(forms.Form):
    DC_CHOICES =(
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
    )
    ATTACCANTI_CHOICES =(
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
    )
    difensori = forms.ChoiceField(choices=DC_CHOICES)
    centrocampisti = forms.ChoiceField(choices=DC_CHOICES)
    attaccanti = forms.ChoiceField(choices=ATTACCANTI_CHOICES)

    def clean(self):
        """Controlla se il modulo selezionato ha un totale di 10 giocatori in campo [escluso il portiere]"""
        difensori = self.cleaned_data['difensori']
        centrocampisti = self.cleaned_data['centrocampisti']
        attaccanti = self.cleaned_data['attaccanti']
        totale = int(difensori)+int(centrocampisti)+int(attaccanti)
        if totale != 10:
            raise ValidationError('La somma totale non equivale a 10.')
        return super().clean()
  

class TitolariForm(forms.Form):
    giocatore = forms.ModelChoiceField(queryset=Giocatore.objects.none())

    def __init__(self, *args, **kwargs):
        squadra = kwargs.pop('squadra', None)
        ruolo = kwargs.pop('ruolo', None)

        super(TitolariForm, self).__init__(*args, **kwargs)
        self.fields['giocatore'].queryset = Giocatore.objects.filter(squadra=squadra).filter(ruolo=ruolo)
