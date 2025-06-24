import os
import django
import random
from faker import Faker
from datetime import datetime, timedelta, time, date


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from crm_app.models import (
    UserProfile, Doctor, Reception, Department, Speciality, DoctorServices,
    Patient, Payment, CustomerRecord, HistoryRecord, PriceList, Analytics
)

fake = Faker('ru_RU')

def create_departments(n=3):
    return [Department.objects.create(department_name=fake.job()) for _ in range(n)]

def create_specialities(n=3):
    return [Speciality.objects.create(speciality_title=fake.catch_phrase()) for _ in range(n)]

def create_receptions(specialities, n=2):
    receptions = []
    for _ in range(n):
        user = Reception.objects.create_user(
            email=fake.unique.email(),
            password='12345678',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone_number=fake.phone_number(),
            role='Reception',
            gender=random.choice(['Male', 'Female']),
            profile_picture='profile_images/default.jpg',
        )
        user.speciality = random.choice(specialities)
        user.save()
        receptions.append(user)
    return receptions


def create_doctors(departments, specialities, n=3):
    doctors = []
    for _ in range(n):
        speciality = random.choice(specialities)
        department = random.choice(departments)

        doctor = Doctor.objects.create_user(
            email=fake.unique.email(),
            password='12345678',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone_number=fake.phone_number(),
            role='Doctor',
            gender=random.choice(['Male', 'Female']),
            profile_picture='profile_images/default.jpg',
            medical_license=fake.uuid4(),
            bonus='5%',
            cabinet=str(random.randint(101, 110)),
            speciality=speciality,  # ← добавлено
            department=department  # ← добавлено
        )
        doctors.append(doctor)
    return doctors

def create_services(doctors, departments, n=5):
    services = []
    for _ in range(n):
        service = DoctorServices.objects.create(
            doctor_service=fake.word(),
            department=random.choice(departments),
            price=random.randint(500, 5000),
            discount=random.uniform(0, 0.3),
            salary_doctor=random.randint(100, 1000),
            service_label=fake.lexify('????')
        )
        services.append(service)
    return services

def create_patients(doctors, services, departments, receptions, n=10):
    patients = []
    for _ in range(n):
        patient = Patient.objects.create(
            full_name=fake.name(),
            phone_number=fake.phone_number(),
            doctor_service=random.choice(services),
            birthday=fake.date_of_birth(minimum_age=1, maximum_age=80),
            department=random.choice(departments),
            reception=random.choice(receptions),
            started_time=time(hour=random.randint(8, 10)),
            end_time=time(hour=random.randint(11, 14)),
            gender_patient=random.choice(['Male', 'Female']),
            doctor=random.choice(doctors),
            status_patient=random.choice(['Живая очередь', 'Предзапись', 'Отмененные']),
            appointment_date=date.today()
        )
        patients.append(patient)
    return patients

def create_payments(patients, doctors, services):
    payments = []
    for patient in patients:
        payment = Payment.objects.create(
            patient=patient,
            doctor=patient.doctor,
            service=random.choice(services),
            payment_type=random.choice(['cash', 'card'])
        )
        payments.append(payment)
    return payments


def random_time(start=8, end=18):
    hour = random.randint(start, end - 1)
    minute = random.choice([0, 15, 30, 45])
    return time(hour=hour, minute=minute)

def create_customer_records(patients, receptions, departments, payments, services):
    for i in range(len(patients)):
        started = random_time()
        end = (datetime.combine(date.today(), started) + timedelta(minutes=30)).time()

        CustomerRecord.objects.create(
            reception=random.choice(receptions),
            department=random.choice(departments),
            change=random.randint(0, 100),
            phone_number=payments[i].patient.phone_number,
            started_time=started,
            end_time=end,
            payment_type=payments[i],
            doctor_ser=random.choice(services),
            doctor=payments[i].doctor,
            patient=payments[i].patient,
        )

def create_history_records(patients, receptions, departments, doctors, services, payments):
    for i in range(len(patients)):
        HistoryRecord.objects.create(
            patient=patients[i],
            reception=random.choice(receptions),
            departament=random.choice(departments),
            doctor=doctors[i % len(doctors)],
            service=random.choice(services),
            record=random.choice(['был в приеме', 'в ожидании', 'отменен']),
            payment=CustomerRecord.objects.order_by('?').first(),
            description=fake.sentence()
        )

def create_price_lists(departments, services):
    for _ in range(5):
        PriceList.objects.create(
            department=random.choice(departments),
            service=random.choice(services)
        )

def create_analytics(patients, services):
    for _ in range(10):
        Analytics.objects.create(
            patient=random.choice(patients),
            service=random.choice(services)
        )

def run():
    Department.objects.all().delete()
    Speciality.objects.all().delete()
    Reception.objects.all().delete()
    Doctor.objects.all().delete()
    DoctorServices.objects.all().delete()
    Patient.objects.all().delete()
    Payment.objects.all().delete()
    CustomerRecord.objects.all().delete()
    HistoryRecord.objects.all().delete()
    PriceList.objects.all().delete()
    Analytics.objects.all().delete()

    print("Создание данных...")

    departments = create_departments()
    specialities = create_specialities()
    receptions = create_receptions(specialities)
    doctors = create_doctors(departments, specialities)
    services = create_services(doctors, departments)
    patients = create_patients(doctors, services, departments, receptions)
    payments = create_payments(patients, doctors, services)
    create_customer_records(patients, receptions, departments, payments, services)
    create_history_records(patients, receptions, departments, doctors, services, payments)
    create_price_lists(departments, services)
    create_analytics(patients, services)

    print("🎉 Данные успешно засеяны!")

if __name__ == '__main__':
    run()
