from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from gestionesquadra.models import Squadra


class Campionato(models.Model):
    """Campionato Entity"""
    PARTECIPANTI_CHOICES = [(6, '6'), (8, '8'), (10, '10')]
    championship_admin = models.ForeignKey(User, verbose_name='Championship Admin', blank=True, null=True, on_delete=models.CASCADE)
    nome_campionato = models.CharField(max_length=255)
    giornata_corrente = models.IntegerField(default=1)
    partecipanti = models.IntegerField(verbose_name='Partecipanti', default=6, choices=PARTECIPANTI_CHOICES)

    def __str__(self) -> str:
        return f"{self.nome_campionato}"
    
    def clean(self):
        existing_campionato = Campionato.objects.filter(nome_campionato=self.nome_campionato).first()
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
    giocatore = models.ManyToManyField('gestionesquadra.Giocatore', verbose_name='Giocatore', related_name='formazione', blank=True)
    partita = models.ForeignKey(Partita, on_delete=models.CASCADE, verbose_name='Partita', related_name='formazione')
    data_inserimento = models.DateTimeField(auto_now_add=True, verbose_name='Data inserimento formazione', blank=True, null=True)
    squadra = models.ForeignKey(Squadra, on_delete=models.CASCADE, verbose_name='Squadra', related_name='formazione', blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.partita} - {self.get_tipo_display()}"

    class Meta:
        verbose_name_plural = 'Formazioni'


class Voto(models.Model):
    id_voti = models.CharField(max_length=20, blank=True)
    ruolo = models.CharField(max_length=20, blank=True)
    nome_giocatore = models.CharField(max_length=20, blank=True)
    voto = models.CharField(max_length=20, blank=True)
    gf = models.CharField(max_length=20, blank=True)
    gs = models.CharField(max_length=20, blank=True)
    rp = models.CharField(max_length=20, blank=True)
    rs = models.CharField(max_length=20, blank=True)
    rf = models.CharField(max_length=20, blank=True)
    au = models.CharField(max_length=20, blank=True)
    amm = models.CharField(max_length=20, blank=True)
    esp = models.CharField(max_length=20, blank=True)
    ass = models.CharField(max_length=20, blank=True)
    gdv = models.CharField(max_length=20, blank=True)
    gdp = models.CharField(max_length=20, blank=True)
    giornata = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.id_voti}"

    class Meta:
        verbose_name_plural = 'Voti'