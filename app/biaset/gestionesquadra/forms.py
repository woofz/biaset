from django import forms

from gestionecampionato.models import Campionato
from .models import Giocatore, Squadra


class AssociaGiocatoreForm(forms.Form):
    """Form di associazione di un giocatore ad una squadra"""
    giocatore = forms.ModelChoiceField(queryset=Giocatore.objects.none(), required=True)
    squadra = forms.ModelChoiceField(queryset=Squadra.objects.none(), required=True)
    
    def __init__(self, *args, **kwargs):
        campionato = kwargs.pop('campionato', None)
        #squadra = kwargs.pop('squadra', None)

        super(AssociaGiocatoreForm, self).__init__(*args, **kwargs)
        self.fields['giocatore'].queryset = Giocatore.objects.all().exclude(squadra__campionato=campionato)
        self.fields['squadra'].queryset = Squadra.objects.filter(campionato=campionato)
        
    def associaGiocatore(self):
        cd = self.cleaned_data
        giocatore = Giocatore.objects.get(pk=cd['giocatore'].id)
        squadra = Squadra.objects.get(pk=cd['squadra'].id)
        giocatore.squadra.add(squadra)


class InserisciSquadraForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile', None)
        user = kwargs.pop('user', None)
        super(InserisciSquadraForm, self).__init__(*args, **kwargs)


        if profile == 'Championship Admin':
            self.fields['campionato'].queryset = Campionato.objects.all().filter(championship_admin=user)

    class Meta:
        model = Squadra
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }

