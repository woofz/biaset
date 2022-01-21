import django_filters
from .models import Squadra, Giocatore

class FilterSquadra(django_filters.FilterSet):
    
    class Meta:
        model = Giocatore
        fields = ['nome_completo', 'ruolo', 'quotazione']
        
    def my_custom_filter(self, queryset, name, value):
        return queryset.filter(**{
            name: value,
        })