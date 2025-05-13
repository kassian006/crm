import django_filters
from .models import Patient

class PatientFilter(django_filters.FilterSet):
    created_date = django_filters.DateFilter(field_name='created_date', lookup_expr='exact')
    created_date__gte = django_filters.DateFilter(field_name='created_date', lookup_expr='gte')
    created_date__lte = django_filters.DateFilter(field_name='created_date', lookup_expr='lte')

    class Meta:
        model = Patient
        fields = ['created_date', 'created_date__gte', 'created_date__lte']
