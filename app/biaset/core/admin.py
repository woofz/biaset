from django.contrib import admin
from gestioneutenza.models import LeagueAdmin, ChampionshipAdmin, Allenatore, Invito
from gestionecampionato.models import Campionato
from gestionesquadra.models import Squadra, Giocatore

admin.site.register(LeagueAdmin)
admin.site.register(ChampionshipAdmin)
admin.site.register(Allenatore)
admin.site.register(Invito)
admin.site.register(Campionato)
admin.site.register(Squadra)
admin.site.register(Giocatore)
