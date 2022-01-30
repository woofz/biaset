from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User


class Squadra(models.Model):
    nome = models.CharField(max_length=50, verbose_name="Nome squadra", unique=True, validators=[
        RegexValidator(
            regex='^[A-Za-z a-z 0-9]*$',
            message='Il nome della squadra deve essere alfanumerico.',
            code='invalid_squadra'
        ),
    ])
    campionato = models.ForeignKey('gestionecampionato.Campionato', verbose_name="Campionato", on_delete=models.CASCADE)
    allenatore = models.OneToOneField(User, on_delete=models.SET_NULL, verbose_name='Allenatore', blank=True, null=True, related_name='squadra')
    
    def __str__(self):
        return f"{self.nome}"
    
    class Meta:
        verbose_name_plural = 'Squadre'


class Giocatore(models.Model):
    PLAYER_ROLES = [
        ('P', 'Portiere'), 
        ('D', 'Difensore'), 
        ('C', 'Centrocampista'), 
        ('A', 'Attaccante')
    ]
    nome_completo = models.CharField(max_length=255, blank=True, null=True, verbose_name='Cognome')
    ruolo = models.CharField(
        max_length=1,
        choices=PLAYER_ROLES,
        default='T',
        verbose_name='Ruolo',
        blank=True,
        null=True
    )
    id_voti = models.IntegerField(verbose_name='ID Voti Fantacalcio.it')
    quotazione = models.IntegerField(verbose_name='Quotazione', default=0)
    squadra = models.ManyToManyField(Squadra)
    
    def __str__(self) -> str: 
        return f"{self.nome_completo} [{self.ruolo}]"
    
    class Meta:
        verbose_name_plural = 'Giocatori'