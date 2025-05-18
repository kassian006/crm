from .models import *
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserProfileRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'phone_number','password']
        extra_kwargs={'password':{'write_only':True}}

    def create(self, validated_data):
        user=UserProfile.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'email': instance.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }


class ReceptionRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Reception
        fields = ['first_name', 'last_name', 'email', 'phone_number','password']

    def create(self, validated_data):
        validated_data['role'] = 'reception'
        user = Reception.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'email': instance.email,
                'role': instance.role,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }


class DoctorRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Doctor
        fields = ['first_name', 'last_name','speciality', 'medical_license', 'email', 'phone_number', 'password']
        # ВНИМАНИЕ: department здесь нет, как ты просил 'phone_number',

    def create(self, validated_data):
        validated_data['role'] = 'doctor'
        user = Doctor.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'email': instance.email,
                'role': instance.role,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }


class LoginSerializers(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            # 👇 ВОТ ЭТО главное: возвращаем словарь, а не просто user
            return {
                'user': user
            }
        raise serializers.ValidationError("Неверные учетные данные")

    def to_representation(self, validated_data):
        user = validated_data['user']  # теперь тут всё как надо
        refresh = RefreshToken.for_user(user)
        return {
            'user': {
                'email': user.email,
                'role': user.role,  # можно добавить больше инфы, если надо
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, data):
        self.token = data['refresh']
        return data

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except Exception as e:
            raise serializers.ValidationError({'detail': 'Недействительный или уже отозванный токен'})



class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['department_name']

class DepartmentNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['department_name']


class SpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Speciality
        fields = '__all__'


class ReceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reception
        fields = '__all__'


class DoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['first_name', 'last_name']

class NameReceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reception
        fields = ['first_name', 'last_name']


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'role']


class DoctorListSerializer(serializers.ModelSerializer):
    department_name = DepartmentNameSerializer(source='department', read_only=True)
    class Meta:
        model = Doctor
        fields = ['id', 'first_name', 'last_name', 'cabinet', 'department_name', 'phone_number']


class DoctorNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['first_name', 'cabinet']


class DoctorServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorServices
        fields = '__all__'


class DoctorNameServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorServices
        fields = ['doctor_service']

class NameDoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['first_name', 'last_name']


class HistoryRecordInfoPatSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryRecord
        fields = ['record']


class HistoryRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryRecord
        fields = '__all__'


class PatientSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(format="%d %m %Y %H:%M")
    model = Patient
    fields = ['full_name', 'phone_number', 'doctor_service', 'birthday', 'department', 'reception',
              'started_time', 'end_time', 'gender_patient', 'doctor', 'status_patient', 'created_date']


class MakeDoctorServicesSerializer(serializers.ModelSerializer):
    services = DepartmentSerializer()
    class Meta:
        model = DoctorServices
        fields = ['doctor_service', 'price', 'services']


class Make1DoctorServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorServices
        fields = ['doctor_service']


class Make2DoctorServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorServices
        fields = ['doctor_service', 'price']


class MakeAppointmentInfoPatientSerializer(serializers.ModelSerializer):
    reception_patient = NameReceptionSerializer()
    doctor_patient = NameDoctorSerializer()
    department_patient = DepartmentSerializer()
    services = MakeDoctorServicesSerializer()
    class Meta:
        model = Patient
        fields = ['full_name', 'reception_patient', 'doctor_patient', 'started_time', 'end_time', 'status_patient', 'department_patient', 'services']


class HistoryRecordInfoPatientSerializer(serializers.ModelSerializer):
    reception_patient = NameReceptionSerializer()
    doctor_patient = NameDoctorSerializer()
    department_patient = DepartmentSerializer()
    services = Make1DoctorServicesSerializer()
    record = HistoryRecordInfoPatSerializer()
    count_record = serializers.SerializerMethodField()
    count_record_history = serializers.ModelSerializer()
    class Meta:
        model = Patient
        fields = ['full_name', 'reception_patient', 'doctor_patient', 'created_date', 'department_patient',
                  'services', 'record', 'count_record', 'count_record', 'count_record_history']

    def get_count_record(self, obj):
            return obj.get_count_record()

    def get_count_record_history(self, obj):
        return obj.get_count_record_history()


class HistoryReceptionInfoPatientSerializer(serializers.ModelSerializer):
    reception_patient = NameReceptionSerializer()
    doctor_patient = NameDoctorSerializer()
    department_patient = DepartmentSerializer()
    services = Make1DoctorServicesSerializer()
    record = HistoryRecordInfoPatSerializer()
    count_record = serializers.SerializerMethodField()
    count_record_history = serializers.ModelSerializer()
    class Meta:
        model = Patient
        fields = ['full_name', 'reception_patient', 'doctor_patient', 'created_date', 'department_patient', 'services', 'record', 'count_record', 'count_record_history']

    def get_count_record(self, obj):
            return obj.get_count_record()

    def get_count_record_history(self, obj):
        return obj.get_count_record_history()

class PatientNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['full_name']


class CustomerRecordSerializer(serializers.ModelSerializer):
    reception_detail = ReceptionSerializer(source='reception', read_only=True)
    patient_detail = PatientSerializer(source='patient', read_only=True)
    doctor_detail = DoctorProfileSerializer(source='doctor', read_only=True)
    service_detail = DoctorServicesSerializer(source='service', read_only=True)
    department_detail = DepartmentSerializer(source='department', read_only=True)

    class Meta:
        model = CustomerRecord
        fields = ['reception_detail', 'patient_detail', 'doctor_detail', 'service_detail', 'department_detail', 'price', 'change',
                  'payment_type', 'created_date', 'phone_number', 'created_time']

class CheckRecordSerializer(serializers.ModelSerializer):
    patient_name = PatientNameSerializer(source='patient', read_only=True)
    doctor_name = DoctorNameSerializer(source='doctor', read_only=True)
    service_name = DoctorNameServicesSerializer(source='service', read_only=True)

    class Meta:
        model = CustomerRecord
        fields = ['patient_name', 'doctor_name', 'service_name', 'price', 'change', 'payment_type']


class PaymentInfoPatientSerializer(serializers.ModelSerializer):
    doctor_patient = NameDoctorSerializer()
    department_patient = DepartmentSerializer()
    services = Make2DoctorServicesSerializer()
    patient_customer = CustomerRecordSerializer()
    class Meta:
        model = Patient
        fields = ['full_name', 'doctor_patient', 'created_date', 'department_patient', 'services', 'patient_customer']


class InfoPatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['full_name', 'phone_number', 'gender_patient']



class PriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceList
        fields = '__all__'


class AnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analytics
        fields = '__all__'
