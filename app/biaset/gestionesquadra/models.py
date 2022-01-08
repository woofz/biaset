from django.db import models
from django.db.models.fields import related
from gestionecampionato.models import Campionato

class Squadra(models.Model):
    nome = models.CharField(max_length=50, verbose_name="Nome squadra")
    campionato = models.ForeignKey(Campionato, verbose_name="Campionato", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nome} - {self.campionato.nome_campionato}"
    
    class Meta:
        verbose_name_plural = 'Squadre'


class Giocatore(models.Model):
    nome = models.CharField(max_length=255, blank=True, null=True, verbose_name='Nome')
    cognome = models.CharField(max_length=255, blank=True, null=True, verbose_name='Cognome')
    id_voti = models.IntegerField(verbose_name='ID Voti Fantacalcio.it')
    squadra = models.ManyToManyField(Squadra)
    
    def __str__(self) -> str: 
        return f"{self.nome} {self.cognome}"
    
    class Meta:
        verbose_name_plural = 'Giocatori'