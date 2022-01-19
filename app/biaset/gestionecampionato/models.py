from email.policy import default
from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Campionato(models.Model):
    """Campionato Entity"""
    championship_admin = models.ForeignKey(User, verbose_name='Championship Admin', blank=True, null=True, on_delete=models.CASCADE)
    nome_campionato = models.CharField(max_length=255)
    giornata_corrente = models.IntegerField(default=1)
    max_partecipanti = models.IntegerField(verbose_name='Numero massimo partecipanti', default=10)

    def __str__(self) -> str:
        return f"{self.nome_campionato}"
    
    def clean(self):
        existing_campionato = Campionato.objects.filter(nome_campionato=self.nome_campionato).first()
        if (self.max_partecipanti % 2) != 0:
            raise ValidationError('Il numero di partecipanti deve essere pari.')
        if existing_campionato:
            raise ValidationError('Esiste già un campionato con questo nome.')
    
    class Meta:
        verbose_name_plural = 'Campionati'
        

class Partita(models.Model):
    """Partita Entity"""
    gol_squadra1 = models.IntegerField(default=0, verbose_name='Gol Squadra 1')
    gol_squadra2 = models.IntegerField(default=0, verbose_name='Gol Squadra 2')
    squadra = models.ManyToManyField('gestionesquadra.Squadra', verbose_name='Squadra')
    giornata = models.IntegerField(default=1, verbose_name='Giornata')

    class Meta:
        verbose_name_plural = 'Partite'

    def __str__(self):
        squadra1 = self.squadra.all().first()
        squadra2 = self.squadra.all().last()
        
        return f"{squadra1.campionato} - {squadra1} vs {squadra2}"


class Formazione(models.Model):
    """Formazione Entity"""
    FORMATION_TYPES_CHOICES = [('T', 'Titolari'), ('R', 'Riserve')]
    tipo = models.CharField(
        max_length=2,
        choices=FORMATION_TYPES_CHOICES,
        default='T',
        verbose_name='Gruppo (Titolare/Riserva)'
    )
    giocatore = models.ManyToManyField('gestionesquadra.Giocatore', verbose_name='Giocatore', related_name='giocatore')
    partita = models.ForeignKey(Partita, on_delete=models.CASCADE, verbose_name='Partita', related_name='formazione')
    data_inserimento = models.DateTimeField(auto_now_add=True, verbose_name='Data inserimento formazione', blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.partita} - {self.get_tipo_display()}"

    class Meta:
        verbose_name_plural = 'Formazioni'