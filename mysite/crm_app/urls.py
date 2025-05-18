from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
from .views import *

router = SimpleRouter()
router.register(r'user_profile', UserProfileViewSet, basename='user_profile')
router.register(r'department', DepartmentViewSet, basename='department')
router.register(r'speciality', SpecialityViewSet, basename='speciality')
router.register(r'reception', ReceptionViewSet, basename='reception')
router.register(r'doctor', DoctorViewSet, basename='doctor')
router.register(r'doctor_list', DoctorListViewSet, basename='doctor_list')
router.register(r'doctor_service', DoctorServicesViewSet, basename='doctor_service')
router.register(r'make_appointment_info_patient', MakeAppointmentInfoPatientViewSet, basename='make_appointment_info_patient')
router.register(r'history_record_info', HistoryRecordInfoPatientViewSet, basename='history_record_info')
router.register(r'payment_record_info', PaymentInfoPatientViewSet, basename='payment_record_info')
router.register(r'patient_info', InfoPatientViewSet, basename='patient_info')
router.register(r'customer_record', CustomerRecordViewSet, basename='customer_record')
router.register(r'history_record', HistoryRecordViewSet, basename='history_record')
router.register(r'price_list', PriceListViewSet, basename='price_list')
router.register(r'analytic', AnalyticsViewSet, basename='analytic')

urlpatterns = [
    path('', include(router.urls)),
    path('register/doctor/', DoctorRegisterView.as_view(), name='register-doctor'),
    path('register/reception/', ReceptionRegisterView.as_view(), name='register-reception'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('login/admin/', CustomAdminLoginView.as_view(), name='admin-login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('print_check/', CheckRecordListAPIView.as_view(), name='print_check'),
]