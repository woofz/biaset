from random import choice
from django.core.exceptions import ValidationError
from django import forms
from gestionesquadra.models import Giocatore, Squadra

from gestionecampionato.models import Campionato, Partita, Formazione

class CreaCampionatoForm(forms.ModelForm):

    class Meta:

        model = Campionato
        fields = ('nome_campionato', 'partecipanti', 'championship_admin')
        widgets = {
            'nome_campionato': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 60}),
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
    """Form per l'inserimento della formazione [sia titolare sia riserve]"""
    giocatore = forms.ModelChoiceField(queryset=Giocatore.objects.none(), required=True)
    
    def __init__(self, *args, **kwargs):
        squadra = kwargs.pop('squadra', None)
        ruolo = kwargs.pop('ruolo', None)

        super(TitolariForm, self).__init__(*args, **kwargs)
        self.fields['giocatore'].queryset = Giocatore.objects.filter(squadra=squadra).filter(ruolo=ruolo).exclude()

    def save(self, commit=True, *args, **kwargs):
        """Metodo save personalizzato. Non salva un vero e proprio modello, ma aggiunge la relazione tra Formazione e Giocatore"""
        formazione = kwargs.pop('formazione')
        instance = self.cleaned_data['giocatore']
        formazione.giocatore.add(instance)
        
        return instance


class TitolariFormSet(forms.BaseFormSet):
    """Classe FormSet per il controllo di form multipli per inserimento della formazione"""
    def clean(self):
        """Il metodo serve per la validazione del FormSet

        Raises:
            ValidationError: nel caso in cui il campo fosse vuoto
            ValidationError: nel caso in cui vi sia un giocatore duplicato
        """
        super(TitolariFormSet, self).clean()
        
        lista = list()
        form_size = 0
        
        for form in self.forms:
            cleaned_data = form.cleaned_data
            if not cleaned_data:
                raise ValidationError('Tutti i campi sono obbligatori')
            lista.append(cleaned_data)
            form_size += 1
        lista_senza_duplicati = [dict(t) for t in {tuple(d.items()) for d in lista}]
        
        if form_size > len(lista_senza_duplicati):
            raise ValidationError('Hai inserito giocatori duplicati!')


class RiserveForm(forms.Form):
    """Form per l'inserimento della formazione [sia titolare sia riserve]"""
    giocatore = forms.ModelChoiceField(queryset=Giocatore.objects.none(), required=True)
    
    def __init__(self, *args, **kwargs):
        squadra = kwargs.pop('squadra', None)
        ruolo = kwargs.pop('ruolo', None)
        formazione_titolari = kwargs.pop('titolari', None)

        super(RiserveForm, self).__init__(*args, **kwargs)
        giocatori_per_ruolo = Giocatore.objects.filter(squadra=squadra).filter(ruolo=ruolo)
        self.fields['giocatore'].queryset = giocatori_per_ruolo.exclude(id__in=formazione_titolari.giocatore.all()) # Escludo i titolari dalle scelte delle riserve
        
    def save(self, commit=True, *args, **kwargs):
        """Metodo save personalizzato. Non salva un vero e proprio modello, ma aggiunge la relazione tra Formazione e Giocatore"""
        formazione = kwargs.pop('formazione')
        instance = self.cleaned_data.get('giocatore')
        formazione.giocatore.add(instance)
        
        return instance
    
    
class RiserveFormSet(forms.BaseFormSet):
    """Classe FormSet per il controllo di form multipli per inserimento della formazione"""
    def clean(self):
        """Il metodo serve per la validazione del FormSet

        Raises:
            ValidationError: nel caso in cui il campo fosse vuoto
            ValidationError: nel caso in cui vi sia un giocatore duplicato
        """
        super(RiserveFormSet, self).clean()
        
        lista = list()
        form_size = 0
        
        for form in self.forms:
            cleaned_data = form.cleaned_data
            if cleaned_data:    
                lista.append(cleaned_data)
                form_size += 1
        lista_senza_duplicati = [dict(t) for t in {tuple(d.items()) for d in lista}]
        
        if form_size > len(lista_senza_duplicati):
            raise ValidationError('Hai inserito giocatori duplicati!')