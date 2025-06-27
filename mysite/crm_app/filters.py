import django_filters
from django_filters import FilterSet, CharFilter, DateFilter
from django import forms
from .models import Patient


class PatientFilter(FilterSet):
    created_date = DateFilter(
        field_name='created_date',
        lookup_expr='date',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    doctor = CharFilter(field_name='doctor__first_name', lookup_expr='icontains')

    class Meta:
        model = Patient
        fields = {
            'created_date': ['exact'],  # Фильтр по дате
            'doctor': ['exact'],       # Фильтр по id врача (автоматически)
        }