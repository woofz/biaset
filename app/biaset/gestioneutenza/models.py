from django.db import models
from django.contrib.auth.models import User

class LeagueAdmin(models.Model):
    '''Model describing a League Admin'''
    user = models.OneToOneField(User, verbose_name=("Utente"), on_delete=models.CASCADE)
    nome_profilo = models.CharField(max_length=35, blank=True, null=True, default="League Admin", verbose_name="Profilo")
    
    def __str__(self) -> str:
        return f"{self.user.first_name}, {self.nome_profilo}"
    
    
class ChampionshipAdmin(models.Model):
    '''Model describing a Championship Admin'''
    user = models.OneToOneField(User, verbose_name=("Utente"), on_delete=models.CASCADE)
    nome_profilo = models.CharField(max_length=35, blank=True, null=True, default="Championship Admin", verbose_name="Profilo")
    
    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}, {self.user.nome_profilo}"


class Allenatore(models.Model):
    '''Model describing a Team Coach'''
    user = models.OneToOneField(User, verbose_name=("Utente"), on_delete=models.CASCADE)
    nome_profilo = models.CharField(max_length=35, blank=True, null=True, default="Allenatore", verbose_name="Profilo")
    campionati_vinti = models.IntegerField(default=0, blank=True, null=True)
    # ToDo: add Squadra
    
    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}, {self.user.nome_profilo}"
    
    class Meta:
        verbose_name_plural = 'Allenatori'
        

class Invito(models.Model):
    user = models.ForeignKey(User, verbose_name="Creato da", on_delete=models.CASCADE)
    expire_dt = models.DateTimeField(verbose_name="Data e orario di scadenza")
    codice_invito = models.CharField(max_length=32)
    destinatario = models.CharField(max_length=255, verbose_name="Email destinatario")
    # ToDo: campionatoId

    def __str__(self) -> str:
        return 
    
    class Meta:
        verbose_name_plural = 'Inviti'