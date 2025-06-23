from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
from .views import *

router = SimpleRouter()
router.register(r'user_profile', UserProfileViewSet, basename='user_profile')
router.register(r'department', DepartmentViewSet, basename='department')
router.register(r'speciali  ty', SpecialityViewSet, basename='speciality')
router.register(r'reception', ReceptionViewSet, basename='reception')
router.register(r'doctor', DoctorViewSet, basename='doctor')
router.register(r'doctor_list', DoctorListViewSet, basename='doctor_list')
router.register(r'doctor_service', DoctorServicesViewSet, basename='doctor_service')
router.register(r'history_record_info', HistoryRecordInfoPatientViewSet, basename='history_record_info')
router.register(r'history_reception_info', HistoryReceptionInfoPatientViewSet, basename='history_reception_info')
router.register(r'payment_record_info', PaymentInfoPatientViewSet, basename='payment_record_info')
router.register(r'patient_info', InfoPatientViewSet, basename='patient_info')
router.register(r'payment', PaymentViewSet, basename='payment')
router.register(r'customer_record', CustomerRecordViewSet, basename='customer_record')
router.register(r'calendar_doctor', CalendarViewSet, basename='calendar_doctor')
router.register(r'history_record', HistoryRecordViewSet, basename='history_record')
router.register(r'analytic', AnalyticsViewSet, basename='analytic')

urlpatterns = [
    path('', include(router.urls)),
    path('register/doctor/', DoctorRegisterView.as_view(), name='register-doctor'),
    path('register/reception/', ReceptionRegisterView.as_view(), name='register-reception'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('login/admin/', CustomAdminLoginView.as_view(), name='admin-login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('print_check/', CheckRecordListAPIView.as_view(), name='print_check'),
    path('make_appointment_info_patient/', MakeAppointmentInfoPatientAPIView.as_view(), name='make_appointment_info_patient'),
    path('price_list/', PriceListAPIView.as_view(), name='price_list'),
    path('price_list/<int:pk>/', PriceDetailAPIView.as_view(), name='price_detail'),

]