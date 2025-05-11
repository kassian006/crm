from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'user_profile', UserProfileViewSet, basename='user_profile')
router.register(r'department', DepartmentViewSet, basename='department')
router.register(r'speciality', SpecialityViewSet, basename='speciality')
router.register(r'reception', ReceptionViewSet, basename='reception')
router.register(r'doctor', DoctorViewSet, basename='doctor')
router.register(r'doctor_service', DoctorServicesViewSet, basename='doctor_service')
router.register(r'patient', PatientViewSet, basename='patient')
router.register(r'customer_record', CustomerRecordViewSet, basename='customer_record')
router.register(r'history_record', HistoryRecordViewSet, basename='history_record')
router.register(r'price_list', PriceListViewSet, basename='price_list')
router.register(r'analytic', AnalyticsViewSet, basename='analytic')

urlpatterns = [
    path('', include(router.urls)),
]