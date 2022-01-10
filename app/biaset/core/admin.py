from django.contrib import admin
from gestioneutenza.models import Profilo, Invito
from gestionecampionato.models import Campionato
from gestionesquadra.models import Squadra, Giocatore

admin.site.register(Profilo)
admin.site.register(Invito)
admin.site.register(Campionato)
admin.site.register(Squadra)
admin.site.register(Giocatore)
