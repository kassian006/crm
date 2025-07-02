from rest_framework import viewsets, generics, status
from .serializers import *
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework import filters
from .filters import PatientFilter, ReportFilter, DoctorReportFilter, AllReportFilter
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from django.db.models import Sum, Q
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Report
from .serializers import ReportSerializer
from .models import EmailLoginCode
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
import random
from django.core.mail import send_mail
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import EmailLoginCode
from .serializers import SendLoginCodeSerializer, VerifyLoginCodeSerializer
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
import openpyxl
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, F
from .models import Report
from django.utils.dateparse import parse_date
from openpyxl import Workbook
from django.db.models import Sum
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser

from django.db.models import Count, Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear



@api_view(['POST'])
def send_login_code_view(request):
    serializer = SendLoginCodeSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        code = str(random.randint(100000, 999999))

        # Сохраняем в БД
        EmailLoginCode.objects.create(email=email, code=code)

        # Отправляем на почту
        send_mail(
            'Код для сброса пароля',
            f'Ваш код для сброса пароля: {code}',
            'noreply@example.com',  # может быть EMAIL_HOST_USER
            [email],
            fail_silently=False,
        )

        return Response({'message': 'Код отправлен на почту'}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verify_login_code(request):
    serializer = VerifyLoginCodeSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        try:
            login_code = EmailLoginCode.objects.filter(email=email, code=code).latest('created_at')
        except EmailLoginCode.DoesNotExist:
            return Response({'error': 'Неверный код'}, status=status.HTTP_400_BAD_REQUEST)

        if not login_code.is_valid():
            return Response({'error': 'Код устарел'}, status=status.HTTP_400_BAD_REQUEST)

        # Если код валидный — можно теперь попросить ввести новый пароль (или сразу поменять)
        return Response({'message': 'Код подтвержден. Введите новый пароль.'}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def reset_password_view(request):
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']

        try:
            login_code = EmailLoginCode.objects.filter(email=email, code=code).latest('created_at')
        except EmailLoginCode.DoesNotExist:
            return Response({'error': 'Неверный код'}, status=status.HTTP_400_BAD_REQUEST)

        if not login_code.is_valid():
            return Response({'error': 'Код устарел'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Пароль успешно обновлён'}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomLoginView(TokenObtainPairView):
    serializer_class = LoginSerializers

    def post(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({"detail: Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)

        user=serializer.validated_data
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomAdminLoginView(TokenObtainPairView):
    serializer_class = LoginSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({"detail": "Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data.get('user')

        if not user.is_staff and not user.is_superuser:
            return Response({"detail": "Доступ разрешен только администраторам"},
                            status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh токен отсутствует."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Вы вышли из системы."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": "Ошибка обработки токена."}, status=status.HTTP_400_BAD_REQUEST)



class DoctorListAPIView(generics.ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['department']
    search_fields = ['first_name', 'last_name']


class DoctorDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorDetailSerializer


class DoctorCreateAPIView(generics.CreateAPIView):
    serializer_class = DoctorCreateSerializer
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(request_body=DoctorCreateSerializer)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


    # def create(self, request, *args, **kwargs):
    #     try:
    #         serializer = self.get_serializer(data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         doctor = serializer.save()
    #         return Response(serializer.data, status.HTTP_201_CREATED)
    #     except serializers.ValidationError as e:
    #         return Response({'detail': 'Маалымат туура эмес берилди'}, status.HTTP_400_BAD_REQUEST)
    #     except NameError as e:
    #         return Response({'detail': f'{e}, Ошибка в коде'}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    #     except Exception:
    #         return Response({'detail': 'Сервер не работает'}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class PatientAPIView(generics.CreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class PatientDesktopListAPIView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientDesktopSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = PatientFilter
    search_fields = ['full_name']

class PatientDesktopDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class MakeAppointmentInfoPatientAPIView(generics.CreateAPIView):
    queryset = Patient.objects.select_related('reception', 'doctor', 'department', 'doctor_service').all()
    serializer_class = MakeAppointmentInfoPatientSerializer


class HistoryRecordInfoPatientAPIView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = HistoryRecordInfoPatientSerializer


class HistoryReceptionInfoPatientAPIView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = HistoryReceptionInfoPatientSerializer



class CalendarListAPIView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = CalendarSerializer


class CalendarDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = CalendarSerializer


class CalendarCreateAPIView(generics.CreateAPIView):
    serializer_class = CalendarCreateSerializer


class PaymentInfoPatientListAPIView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = PaymentInfoPatientSerializer


class PaymentInfoPatientDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PaymentInfoPatientSerializer


class InfoPatientAPIView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = InfoPatientSerializer


class CheckRecordListAPIView(generics.ListAPIView):
    queryset = CustomerRecord.objects.all()
    serializer_class = CheckRecordSerializer


class PriceListAPIView(generics.ListAPIView):
    queryset = PriceList.objects.all()
    serializer_class = PriceListSerializer


class PriceDetailAPIView(generics.RetrieveAPIView):
    queryset = PriceList.objects.all()
    serializer_class = PriceDetailSerializer


class ReportListAPIView(APIView):
    def get(self, request):
        queryset = Report.objects.select_related('doctor', 'patient', 'service__department', 'payment')

        # 🔍 Поиск
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(doctor__first_name__icontains=search) |
                Q(doctor__last_name__icontains=search) |
                Q(patient__full_name__icontains=search) |
                Q(service__doctor_service__icontains=search) |
                Q(service__department__department_name__icontains=search)
            )

        # 👨‍⚕️ Фильтр по врачу
        doctor_id = request.GET.get('doctor')
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)

        # 🏥 Фильтр по отделению
        department_id = request.GET.get('department')
        if department_id:
            queryset = queryset.filter(service__department_id=department_id)

        # 📅 Фильтр по датам
        date_from = request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)

        date_to = request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        # 💰 Подсчёты
        total_sum = queryset.aggregate(sum=Sum('service__price'))['sum'] or 0
        cash_sum = queryset.filter(payment__payment_type='cash').aggregate(sum=Sum('service__price'))['sum'] or 0
        card_sum = queryset.filter(payment__payment_type='card').aggregate(sum=Sum('service__price'))['sum'] or 0

        # ⚙️ Сериализация
        serializer = ReportSerializer(queryset, many=True)

        return Response({
            'count': queryset.count(),
            'total_sum': total_sum,
            'cash_sum': cash_sum,
            'card_sum': card_sum,
            'results': serializer.data
        }, status=status.HTTP_200_OK)


class PaymentInfoPatientSumAPIView(APIView):
    def get(self, request):
        data = Payment.get_count_sum()
        serializer = PaymentTypeNameSumSerializer(data)
        return Response(serializer.data)


class HistoryReceptionInfoPatientDefAPIView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = HistoryReceptionInfoPatientTotalSerializer


class HistoryRecordInfoPatientDefAPIView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = HistoryRecordInfoPatientTotalSerializer


class ReportExportExcelView(APIView):
    def get(self, request):
        reports = Report.objects.select_related('doctor', 'patient', 'service', 'payment').all()

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Reports"

        headers = ['ID', 'Date', 'Doctor', 'Patient', 'Service', 'Department', 'Payment Type', 'Price']
        sheet.append(headers)

        for report in reports:
            row = [
                report.id,
                report.date.strftime('%Y-%m-%d'),
                f"{report.doctor.first_name} {report.doctor.last_name}",
                report.patient.full_name,
                report.service.doctor_service,
                report.service.department.department_name,
                report.payment.get_payment_type_display(),
                float(report.service.price)
            ]
            sheet.append(row)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=report.xlsx'
        workbook.save(response)
        return response


class ReportDoctorsAPIViews(generics.ListAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportDoctorsSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = DoctorReportFilter


class SummaryReportView(APIView):
    def get(self, request):
        reports = Report.objects.select_related('payment', 'service', 'doctor', 'patient', 'service__department')

        # 🔎 Search-поиск
        search = request.GET.get('search')
        if search:
            reports = reports.filter(
                Q(doctor__first_name__icontains=search) |
                Q(doctor__last_name__icontains=search) |
                Q(patient__full_name__icontains=search) |
                Q(service__doctor_service__icontains=search) |
                Q(service__department__department_name__icontains=search)
            )

        # 🧪 Применим фильтр дат (AllReportFilter)
        filterset = AllReportFilter(request.GET, queryset=reports)
        if filterset.is_valid():
            reports = filterset.qs
        else:
            return Response(filterset.errors, status=400)

        # 📊 Подсчёты
        total_services = reports.aggregate(sum=Sum('service__price'))['sum'] or 0
        cash_total = reports.filter(payment__payment_type='cash').aggregate(sum=Sum('service__price'))['sum'] or 0
        card_total = reports.filter(payment__payment_type='card').aggregate(sum=Sum('service__price'))['sum'] or 0
        doctor_salary_total = reports.aggregate(sum=Sum('service__salary_doctor'))['sum'] or 0
        doctor_salary_cash = reports.filter(payment__payment_type='cash').aggregate(sum=Sum('service__salary_doctor'))['sum'] or 0
        doctor_salary_card = reports.filter(payment__payment_type='card').aggregate(sum=Sum('service__salary_doctor'))['sum'] or 0
        clinic_cash = cash_total - doctor_salary_cash
        clinic_card = card_total - doctor_salary_card

        return Response({
            "cash_paid": cash_total,
            "card_paid": card_total,
            "total_services": total_services,
            "doctor_salary_total": doctor_salary_total,
            "doctor_salary_cash": doctor_salary_cash,
            "doctor_salary_card": doctor_salary_card,
            "clinic_cash": clinic_cash,
            "clinic_card": clinic_card,
        })


class SummaryReportExportExcelView(APIView):
    def get(self, request):
        reports = Report.objects.select_related('payment', 'service', 'doctor', 'patient', 'service__department')

        # 🔍 Фильтр по поиску
        search = request.GET.get('search')
        if search:
            reports = reports.filter(
                Q(doctor__first_name__icontains=search) |
                Q(doctor__last_name__icontains=search) |
                Q(patient__full_name__icontains=search) |
                Q(service__doctor_service__icontains=search) |
                Q(service__department__department_name__icontains=search)
            )

        # 📅 Фильтр по датам
        filterset = AllReportFilter(request.GET, queryset=reports)
        if filterset.is_valid():
            reports = filterset.qs
        else:
            return Response(filterset.errors, status=400)

        # 📊 Подсчёты
        total_services = reports.aggregate(sum=Sum('service__price'))['sum'] or 0
        cash_total = reports.filter(payment__payment_type='cash').aggregate(sum=Sum('service__price'))['sum'] or 0
        card_total = reports.filter(payment__payment_type='card').aggregate(sum=Sum('service__price'))['sum'] or 0
        doctor_salary_total = reports.aggregate(sum=Sum('service__salary_doctor'))['sum'] or 0
        doctor_salary_cash = reports.filter(payment__payment_type='cash').aggregate(sum=Sum('service__salary_doctor'))['sum'] or 0
        doctor_salary_card = reports.filter(payment__payment_type='card').aggregate(sum=Sum('service__salary_doctor'))['sum'] or 0
        clinic_cash = cash_total - doctor_salary_cash
        clinic_card = card_total - doctor_salary_card

        # 📁 Создаём Excel
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Summary Report"

        sheet.append([
            'Total Services', 'Cash Paid', 'Card Paid',
            'Doctor Salary (Total)', 'Doctor Salary (Cash)', 'Doctor Salary (Card)',
            'Clinic (Cash)', 'Clinic (Card)'
        ])

        sheet.append([
            total_services, cash_total, card_total,
            doctor_salary_total, doctor_salary_cash, doctor_salary_card,
            clinic_cash, clinic_card
        ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=summary_report.xlsx'
        workbook.save(response)
        return response



class AppointmentStatsAPIView(APIView):
    def get(self, request):
        period = request.query_params.get("period", "weekly")

        now = timezone.now().date()
        trunc_map = {
            'daily': TruncDay,
            'weekly': TruncWeek,
            'monthly': TruncMonth,
            'yearly': TruncYear
        }
        delta_map = {
            'daily': 1,
            'weekly': 7,
            'monthly': 30,
            'yearly': 365
        }

        if period not in trunc_map:
            return Response({"error": "Invalid period"}, status=400)

        trunc_func = trunc_map[period]
        start_date = now - timedelta(days=delta_map[period])

        # Основной график
        chart_data = (
            Patient.objects
            .filter(appointment_date__gte=start_date)
            .annotate(period=trunc_func("appointment_date"))
            .values("period")
            .annotate(
                total=Count("id"),
                canceled=Count("id", filter=Q(status_patient='Отмененные'))
            )
            .order_by("period")
        )

        # Общие метрики
        total_doctors = Doctor.objects.count()

        total_patients = Patient.objects.filter(appointment_date__gte=start_date).count()
        unique_patients_set = set()
        repeated = 0
        new = 0

        for p in Patient.objects.filter(appointment_date__gte=start_date).order_by('appointment_date'):
            key = (p.full_name.strip().lower(), str(p.phone_number))
            if key in unique_patients_set:
                repeated += 1
            else:
                unique_patients_set.add(key)
                new += 1

        new_percent = round((new / max(total_patients, 1)) * 100)
        repeated_percent = 100 - new_percent

        # Рост и падение (сравниваем с предыдущим периодом)
        prev_start = start_date - timedelta(days=delta_map[period])
        prev_count = Patient.objects.filter(appointment_date__gte=prev_start, appointment_date__lt=start_date).count()
        current_count = total_patients

        growth = current_count - prev_count
        trend = "up" if growth > 0 else ("down" if growth < 0 else "same")

        return Response({
            "chart": chart_data,
            "total_doctors": total_doctors,
            "total_clients": len(unique_patients_set),
            "new_percent": new_percent,
            "repeated_percent": repeated_percent,
            "growth": growth,
            "trend": trend
        })
