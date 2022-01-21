from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import ModelBase
from django.db.models.fields.related import ManyToManyField
from gestionecampionato.models import Campionato


class Profilo(models.Model):
    nome = models.CharField(max_length=255, verbose_name='Tipo profilo')
    user = ManyToManyField(User, verbose_name='Utente', blank=True, related_name='user')

    class Meta:
        verbose_name_plural = "Profili"

    def __str__(self) -> str:
        return self.nome


class Invito(models.Model):
    user = models.ForeignKey(User, verbose_name="Creato da", on_delete=models.CASCADE)
    expire_dt = models.DateTimeField(verbose_name="Data e orario di scadenza")
    codice_invito = models.CharField(max_length=32)
    destinatario = models.CharField(max_length=255, verbose_name="Email destinatario")
    campionato = models.ForeignKey(Campionato, verbose_name='Campionato', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.destinatario}, {self.codice_invito}"
    
    class Meta:
        verbose_name_plural = 'Inviti'