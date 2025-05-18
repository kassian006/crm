import django_filters
from django import forms
from .models import Patient

class PatientFilter(django_filters.FilterSet):
    created_date = django_filters.DateFilter(
        field_name='created_date',
        lookup_expr='date',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Patient
        fields = ['created_date']
