from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models

ROLE_CHOICES = (
    ('Admin', 'admin'),
    ('Reception', 'reception'),
    ('Doctor', 'doctor')
)
GENDER_CHOICES = (
    ('Male', 'male'),
    ('Female', 'female')
)


class UserProfile(AbstractUser):
    phone_number = PhoneNumberField(null=True, blank=True)
    full_name = models.CharField(max_length=150)
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),
                                                       MaxValueValidator(140)],
                                           null=True, blank=True)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profile_images/')
    gender = models.CharField(max_length=32, choices=GENDER_CHOICES)
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)

    def __str__(self):
        return f'{self.full_name}'


class Department(models.Model):
    department_name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.department_name}'


class Speciality(models.Model):
    speciality_title = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.speciality_title}'


class Reception(UserProfile):
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE, related_name='speciality_reception')


class Doctor(UserProfile):
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE, related_name='speciality_doctor')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='department_doctor')
    image = models.ImageField(upload_to='doctor_image/', null=True, blank=True)
    medical_linense = models.CharField(max_length=50)
    bonus = models.CharField(max_length=27, null=True, blank=True)
    cabinet = models.CharField(max_length=5, null=True, blank=True)


class DoctorServices(models.Model):
    doctor_service = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="services")
    price = models.PositiveIntegerField(default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    salary_doctor = models.PositiveSmallIntegerField()

    def get_discount_price(self):
        return self.price * (1 - self.discount)


class Patient(models.Model):
    phone_number = PhoneNumberField(null=True, blank=True)
    doctor_service = models.ForeignKey(DoctorServices, on_delete=models.CASCADE, related_name='service_doctor')
    birthday = models.DateField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='department_patient')
    reception = models.ForeignKey(Reception, on_delete=models.CASCADE, related_name='reception_patient')
    started_time = models.TimeField()
    end_time = models.TimeField()
    gender_patient = models.CharField(max_length=32, choices=GENDER_CHOICES)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_patient')
    STATUS_CHOICES = (
        ('Живая очередь', 'Живая очередь'),
        ('Предзапись', 'Предзапись'),
        ('Отмененные', 'Отмененные')
    )
    status_patient = models.CharField(max_length=32, choices=STATUS_CHOICES)
    created_date = models.DateField()


class CustomerRecord(models.Model):
    reception = models.ForeignKey(Reception, related_name='reception_customer', on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_customer')
    doctor = models.ForeignKey(Doctor, related_name='doctor_customer', on_delete=models.CASCADE)
    service = models.ForeignKey(DoctorServices, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    price = models.PositiveIntegerField(default=0)
    change = models.PositiveIntegerField()
    PAYMENT_CHOICES = (
        ('cash', 'Наличные'),
        ('card', 'Карта'),
    )
    payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cash')
    date = models.DateTimeField(auto_now_add=True)
    phone_number = PhoneNumberField(region='KG', null=True, blank=True)
    time = models.TimeField()  # расширение времени
    #  инфо о пациенте ушул класс мн берилет
    # сериалайзерге релитетнейм  мн доктордын ичинен запистерди фильтр кылуу

    def __str__(self):
        return f"Invoice for {self.patient}"


class HistoryRecord(models.Model):
    patient = models.ForeignKey(Patient, related_name='patient_history', on_delete=models.CASCADE)
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

class PriceList(models.Model):
    department = models.ForeignKey(Department, related_name='departament_price_list', on_delete=models.CASCADE)
    service = models.ForeignKey(DoctorServices, related_name='price_service', on_delete=models.CASCADE)


class Analytics(models.Model):
    date = models.DateField(auto_now_add=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_analytics')
    service = models.ForeignKey(DoctorServices, on_delete=models.CASCADE, related_name='service_analytics')














