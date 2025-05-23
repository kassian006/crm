from rest_framework import viewsets, generics, status
from .serializers import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .filters import PatientFilter
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response


class UserProfileRegisterView(generics.CreateAPIView):
    serializer_class = UserProfileRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DoctorRegisterView(generics.CreateAPIView):
    serializer_class = DoctorRegisterSerializer


class ReceptionRegisterView(generics.CreateAPIView):
    serializer_class = ReceptionRegisterSerializer


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

    def get_queryset(self):
        return UserProfile.objects.filter(user__id=self.request.user.id)

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


class DoctorListViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['department']
    search_fields = ['first_name', 'last_name']


class DoctorServicesViewSet(viewsets.ModelViewSet):
    queryset = DoctorServices.objects.all()
    serializer_class = MakeDoctorServicesSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PatientFilter


class MakeAppointmentInfoPatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = MakeAppointmentInfoPatientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PatientFilter


class HistoryRecordInfoPatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = HistoryRecordInfoPatientSerializer


class PaymentInfoPatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PaymentInfoPatientSerializer

class InfoPatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = InfoPatientSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class CustomerRecordViewSet(viewsets.ModelViewSet):
    queryset = CustomerRecord.objects.all()
    serializer_class = CustomerRecordSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PatientFilter

class CheckRecordListAPIView(generics.ListAPIView):
    queryset = CustomerRecord.objects.all()
    serializer_class = CheckRecordSerializer


class HistoryRecordViewSet(viewsets.ModelViewSet):
    queryset = HistoryRecord.objects.all()
    serializer_class = HistoryRecordSerializer


class PriceListViewSet(viewsets.ModelViewSet):
    queryset = PriceList.objects.all()
    serializer_class = PriceListSerializer


class AnalyticsViewSet(viewsets.ModelViewSet):
    queryset = Analytics.objects.all()
    serializer_class = AnalyticsSerializer

