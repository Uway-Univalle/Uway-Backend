import django_filters
from trips.models import Trip

class TripFilter(django_filters.FilterSet):
    date_after = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_before = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    status = django_filters.CharFilter(field_name='status', lookup_expr='iexact')
    route = django_filters.NumberFilter(field_name='route__id')
    driver = django_filters.NumberFilter(field_name='driver__id')

    class Meta:
        model = Trip
        fields = ['status', 'route', 'driver', 'date_after', 'date_before']