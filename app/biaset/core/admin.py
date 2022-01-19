from django.contrib import admin
from gestioneutenza.models import Profilo, Invito
from gestionecampionato.models import Campionato, Partita, Formazione
from gestionesquadra.models import Squadra, Giocatore

admin.site.site_header = 'BiaSet Management'

admin.site.register(Profilo)
admin.site.register(Invito)
admin.site.register(Campionato)
admin.site.register(Squadra)
admin.site.register(Giocatore)
admin.site.register(Partita)
admin.site.register(Formazione)
