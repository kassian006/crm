import django_filters
from django import forms
from .models import Patient, Report, Department, Doctor
from django_filters import FilterSet, DateFilter, CharFilter



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


class ReportFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name="date", lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name="date", lookup_expr='lte')
    doctor = django_filters.NumberFilter(field_name="doctor_id")
    department = django_filters.NumberFilter(field_name="service__department_id")

    class Meta:
        model = Report
        fields = ['doctor', 'department', 'date_from', 'date_to']


class DoctorReportFilter(FilterSet):
    date = DateFilter(
        field_name='date',
        lookup_expr='exact',
        label='Дата отчёта',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    doctor_name = CharFilter(
        field_name='doctor__first_name',
        lookup_expr='icontains',
        label='Имя врача'
    )

    class Meta:
        model = Report
        fields = ['date', 'doctor_name']

class AllReportFilter(FilterSet):
    class Meta:
        model = Report
        fields = {
            'date': ['gt', 'lt'],
        }
