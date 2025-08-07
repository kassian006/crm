from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Case, When, DecimalField, F


ROLE_CHOICES = (
    ('Admin', 'admin'),
    ('Reception', 'reception'),
    ('Doctor', 'doctor')
)
GENDER_CHOICES = (
    ('Male', 'male'),
    ('Female', 'female')
)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("У суперпользователя должен быть is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("У суперпользователя должен быть is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class EmailLoginCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() < self.created_at + timedelta(minutes=5)  # 5 минут срок



class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(region='KG')
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(140)],
                                           null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_images/')
    gender = models.CharField(max_length=32, choices=GENDER_CHOICES)
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.email}'


class Department(models.Model):
    department_name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.department_name}'


class Speciality(models.Model):
    speciality_title = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.speciality_title}'


class Reception(UserProfile):
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE, related_name='speciality_reception', null=True, blank=True)
    class Meta:
        verbose_name = 'Reception'


class Doctor(UserProfile):
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE, related_name='speciality_doctor')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='department_doctor', null=True, blank=True)
    image = models.ImageField(upload_to='doctor_image/', null=True, blank=True)
    medical_license = models.CharField(max_length=50)
    bonus = models.CharField(max_length=27, null=True, blank=True)
    cabinet = models.CharField(max_length=5, null=True, blank=True)

    def __str__(self):
        return f'{self.first_name}, {self.speciality}'

    class Meta:
        verbose_name = 'Doctor'


class DoctorServices(models.Model):
    doctor_service = models.CharField(max_length=256)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="department_services")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    salary_doctor = models.PositiveSmallIntegerField()
    service_label = models.CharField(max_length=10, null=True, blank=True)  # Новое поле для метки, например "FLY"

    def __str__(self):
        return f'{self.doctor_service}, {self.department}'


    def get_discount_price(self):
        return self.price * (1 - self.discount)


class Payment(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='doctor_customer', on_delete=models.CASCADE)
    service = models.ForeignKey(DoctorServices, on_delete=models.SET_NULL, null=True)
    PAYMENT_CHOICES = (
        ('cash', 'cash'),
        ('card', 'card'),
    )
    payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cash')

    def __str__(self):
        return f'{self.payment_type}'

    @classmethod
    def get_count_sum(cls):
        """Получить сумму оплат по типу оплаты (наличные/карта) с учетом скидок"""
        cash_total = 0
        card_total = 0

        for payment in cls.objects.select_related('service').all():
            if payment.service:  # Check if service is not None
                price = payment.service.price * (1 - payment.service.discount)  # Apply discount
                if payment.payment_type == 'cash':
                    cash_total += price
                elif payment.payment_type == 'card':
                    card_total += price

        return {
            "total": cash_total + card_total,
            "cash": cash_total,
            "card": card_total
        }


class Patient(models.Model):
    full_name = models.CharField(max_length=256)
    phone_number = PhoneNumberField(null=True, blank=True)
    doctor_service = models.ForeignKey(DoctorServices, on_delete=models.CASCADE, related_name='service_doctor')
    birthday = models.DateField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='department_patient')
    reception = models.ForeignKey(Reception, on_delete=models.CASCADE, related_name='reception_patient')
    started_time = models.TimeField()
    end_time = models.TimeField()
    gender_patient = models.CharField(max_length=32, choices=GENDER_CHOICES)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='payment_customer', null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_patient')
    STATUS_CHOICES = (
        ('Живая очередь', 'Живая очередь'),
        ('Предзапись', 'Предзапись'),
        ('Отмененные', 'Отмененные')
    )
    status_patient = models.CharField(max_length=32, choices=STATUS_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True)
    descriptions = models.TextField()
    appointment_date = models.DateField(auto_now_add=True)  # Новое поле для даты записи
    appointment_time = models.TimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f'{self.full_name}, {self.status_patient}'

    @classmethod
    def get_count_record(cls):
        """Получить статистику по всем пациентам"""
        all_patients = cls.objects.all()
        status_list = [patient.status_patient for patient in all_patients]

        return {
            "total": len(status_list),
            "pred_records": len([status for status in status_list if status == 'Предзапись']),
            "live_records": len([status for status in status_list if status == 'Живая очередь']),
            "canceled_records": len([status for status in status_list if status == 'Отмененные']),
        }

    @classmethod
    def get_count_reception(cls):
        """Получить статистику по пациентам: Предзапись и Живая очередь"""
        all_patients = cls.objects.all()
        status_list = [patient.status_patient for patient in all_patients]

        pred = [status for status in status_list if status == 'Предзапись']
        live = [status for status in status_list if status == 'Живая очередь']
        canceled = [status for status in status_list if status == 'Отмененные']

        return {
            "total": len(pred) + len(live),
            "pred_records": len(pred),
            "live_records": len(live),
            "canceled_records": len(canceled),
        }
    # def get_count_record(self):
    #     return self.patient_history.count()
    #
    # def get_count_record_history(self):
    #     return {
    #         "total": self.patient_history.count(),
    #         "pred_records": self.patient_history.filter(record='в ожидании').count(),
    #         "live_records": self.patient_history.filter(record='был в приеме').count(),
    #         "canceled_records": self.patient_history.filter(record='отменен').count()
    #     }

class CustomerRecord(models.Model):
    reception = models.ForeignKey(Reception, related_name='reception_customer', on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    change = models.PositiveIntegerField(null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    phone_number = PhoneNumberField(region='KG', null=True, blank=True)
    started_time = models.TimeField()
    end_time = models.TimeField()
    payment_type = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='payment_type_cash')
    doctor_ser = models.ForeignKey(DoctorServices, related_name='doctor_ser', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name='customer_record_doctor', on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, related_name='patient_record', on_delete=models.CASCADE)

    #  инфо о пациенте ушул класс мн берилет
    # сериалайзерге релитетнейм  мн доктордын ичинен запистерди фильтр кылуу

    def __str__(self):
        return f"Invoice for CustomerRecord - {self.reception} - {self.department} - {self.payment_type} "


class HistoryRecord(models.Model):
    patient = models.ForeignKey(Patient, related_name='patient_history', on_delete=models.CASCADE, db_index=True)
    reception = models.ForeignKey(Reception, related_name='reception_history', on_delete=models.CASCADE)
    departament = models.ForeignKey(Department, related_name='departament_history', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name='doctor_history', on_delete=models.CASCADE)
    service = models.ForeignKey(DoctorServices, related_name='service_history', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    CHOICES_RECORD = (
        ('был в приеме', 'был в приеме'),  #был в приеме фильтрация
        ('в ожидании', 'в ожидании'),
        ('отменен', 'отменен'),
    )
    record = models.CharField(max_length=32, choices=CHOICES_RECORD, default='в ожидании')
    payment = models.ForeignKey(CustomerRecord, related_name='payment_history', on_delete=models.CASCADE)
    description = models.TextField()

#     инфо о пациенте - оплата , тип и сумманы чыгарабыз

    def __str__(self):
        return f' HistoryRecord {self.reception}, {self.patient}'


class PriceList(models.Model):
    department = models.ForeignKey(Department, related_name='departament_price_list', on_delete=models.CASCADE)
    service = models.ForeignKey(DoctorServices, related_name='price_service', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.department}, {self.service}'


class Report(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='doctor_report', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    patient = models.ForeignKey(Patient, related_name='patient_report', on_delete=models.CASCADE, db_index=True)
    service = models.ForeignKey(DoctorServices, related_name='service_report', on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, related_name='payment_report', on_delete=models.CASCADE)

