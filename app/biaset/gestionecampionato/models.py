from django.db import models

class Campionato(models.Model):
    nome_campionato = models.CharField(max_length=255)
    giornata_corrente = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.nome_campionato}, giornata {self.giornata_corrente}"
    
    class Meta:
        verbose_name_plural = 'Campionati'