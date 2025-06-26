import django_filters
from django import forms
from .models import Patient, Report

class PatientFilter(django_filters.FilterSet):
    created_date = django_filters.DateFilter(
        field_name='created_date',
        lookup_expr='date',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Patient
        fields = ['created_date']


class ReportFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name="date", lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name="date", lookup_expr='lte')
    doctor = django_filters.NumberFilter(field_name="doctor__id")
    department = django_filters.NumberFilter(field_name="service__department__id")

    class Meta:
        model = Report
        fields = ['doctor', 'department', 'date_from', 'date_to']
