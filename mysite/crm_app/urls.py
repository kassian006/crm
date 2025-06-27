from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
# from .views import PaymentInfoPatientSumAPIView
from .views import *
from .views import ReportExportExcelView


router = SimpleRouter()
router.register(r'user_profile', UserProfileViewSet, basename='user_profile')
router.register(r'department', DepartmentViewSet, basename='department')
router.register(r'speciality', SpecialityViewSet, basename='speciality')
router.register(r'reception', ReceptionViewSet, basename='reception')
router.register(r'doctor', DoctorViewSet, basename='doctor')
router.register(r'doctor_list', DoctorListViewSet, basename='doctor_list')
router.register(r'doctor_service', DoctorServicesViewSet, basename='doctor_service')
router.register(r'payment', PaymentViewSet, basename='payment')
router.register(r'customer_record', CustomerRecordViewSet, basename='customer_record')
router.register(r'calendar_doctor', CalendarViewSet, basename='calendar_doctor')
router.register(r'history_record', HistoryRecordViewSet, basename='history_record')
router.register(r'report', ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
    path('send-code/', send_login_code_view, name='send-login-code'),
    path('verify-code/', verify_login_code, name='verify-login-code'),
    path('reset-password/', reset_password_view, name='reset-password'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('login/admin/', CustomAdminLoginView.as_view(), name='admin-login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('print_check/', CheckRecordListAPIView.as_view(), name='print_check'),
    path('admins/make_appointment_info_patient/', MakeAppointmentInfoPatientAPIView.as_view(), name='make_appointment_info-patient'),
    path('admins/price_list/', PriceListAPIView.as_view(), name='price_list'),
    path('admins/price_list/<int:pk>/', PriceDetailAPIView.as_view(), name='price_detail'),
    path('def/sum/', PaymentInfoPatientSumAPIView.as_view(), name='payment-sum'),
    path('def/total_count/', HistoryReceptionInfoPatientDefAPIView.as_view(), name='payment-total_count'),
    path('def/total_count_will/', HistoryRecordInfoPatientDefAPIView.as_view(), name='payment-total_count'),
    path('admins/history_record_info/', HistoryRecordInfoPatientAPIView.as_view(), name='history_record-info'),
    path('admins/history_reception_info/', HistoryReceptionInfoPatientAPIView.as_view(), name='history_reception-info'),
    path('admins/payment_record_info/', PaymentInfoPatientAPIView.as_view(), name='payment_record-info'),
    path('admins/patient_info/', InfoPatientAPIView.as_view(), name='patient-info'),
    path('export_excel/', ReportExportExcelView.as_view(), name='report-export-excel'),
    path('admins/patient_list/', PatientDesktopListAPIView.as_view(), name='patient-list'),
    path('admins/patient_list/<int:pk>/', PatientDesktopDetailAPIView.as_view(), name='patient-detail'),
    path('admins/patient/', PatientAPIView.as_view(), name='patient-lis'),

]