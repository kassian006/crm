from rest_framework import viewsets, generics, status
from .serializers import *
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework import filters
from .filters import PatientFilter, ReportFilter
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from django.db.models import Sum, Q
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Report
from .serializers import ReportSerializer
from .models import EmailLoginCode
from .serializers import SendLoginCodeSerializer
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
import io
from django.http import HttpResponse
import pandas as pd
import openpyxl
from rest_framework.filters import OrderingFilter, SearchFilter


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


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    # def get_queryset(self):
    #     return UserProfile.objects.filter(user__id=self.request.user.id)

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class SpecialityViewSet(viewsets.ModelViewSet):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer


class ReceptionViewSet(viewsets.ModelViewSet):
    queryset = Reception.objects.all()
    serializer_class = ReceptionSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorProfileSerializer

    def get_queryset(self):
        return Doctor.objects.filter(pk=self.request.user.pk)


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


class DoctorServicesViewSet(viewsets.ModelViewSet):
    queryset = DoctorServices.objects.all()
    serializer_class = MakeDoctorServicesSerializer


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


class MakeAppointmentInfoPatientAPIView(generics.ListCreateAPIView):
    queryset = Patient.objects.select_related('reception', 'doctor', 'department', 'doctor_service').all()
    serializer_class = MakeAppointmentInfoPatientSerializer


class HistoryRecordInfoPatientAPIView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = HistoryRecordInfoPatientSerializer


class HistoryReceptionInfoPatientAPIView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = HistoryReceptionInfoPatientSerializer



class CalendarViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = CalendarSerializer


class PaymentInfoPatientAPIView(generics.RetrieveUpdateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PaymentInfoPatientSerializer

class InfoPatientAPIView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = InfoPatientSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class CustomerRecordViewSet(viewsets.ModelViewSet):
    queryset = CustomerRecord.objects.all()
    serializer_class = CustomerRecordSerializer
    filter_backends = [DjangoFilterBackend]
    # filterset_class = PatientFilter

class CheckRecordListAPIView(generics.ListAPIView):
    queryset = CustomerRecord.objects.all()
    serializer_class = CheckRecordSerializer


class HistoryRecordViewSet(viewsets.ModelViewSet):
    queryset = HistoryRecord.objects.all()
    serializer_class = HistoryRecordSerializer


class PriceListAPIView(generics.ListAPIView):
    queryset = PriceList.objects.all()
    serializer_class = PriceListSerializer


class PriceDetailAPIView(generics.RetrieveAPIView):
    queryset = PriceList.objects.all()
    serializer_class = PriceDetailSerializer


from django.db.models import Sum
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework import status

class ReportViewSet(ReadOnlyModelViewSet):
    queryset = Report.objects.select_related('doctor', 'patient', 'service__department', 'payment')
    serializer_class = ReportSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        request = self.request

        # 👨‍⚕️ Фильтр по врачу
        doctor_id = request.query_params.get('doctor')
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)

        # 🏥 Фильтр по отделению (через service)
        department_id = request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(service__department_id=department_id)

        # 📅 Фильтр по дате (от и до)
        date_from = request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)

        date_to = request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Подсчёты
        total_sum = queryset.aggregate(sum=Sum('service__price'))['sum'] or 0
        cash_sum = queryset.filter(payment__payment_type='cash').aggregate(sum=Sum('service__price'))['sum'] or 0
        card_sum = queryset.filter(payment__payment_type='card').aggregate(sum=Sum('service__price'))['sum'] or 0

        # Пагинация
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data).data
            return Response({
                **paginated_data,
                'total_sum': total_sum,
                'cash_sum': cash_sum,
                'card_sum': card_sum,
            })

        serializer = self.get_serializer(queryset, many=True)
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
