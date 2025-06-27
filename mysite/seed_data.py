import os
import django
import random
from faker import Faker
from datetime import datetime, timedelta, time, date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from crm_app.models import (
    UserProfile, Doctor, Reception, Department, Speciality, DoctorServices,
    Patient, Payment, CustomerRecord, HistoryRecord, PriceList, Report
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
            speciality=random.choice(specialities)
        )
        receptions.append(user)
    return receptions


def create_doctors(departments, specialities, n=3):
    doctors = []
    for _ in range(n):
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
            speciality=random.choice(specialities),
            department=random.choice(departments)
        )
        doctors.append(doctor)
    return doctors


def create_services(departments, n=5):
    services = []
    for _ in range(n):
        service = DoctorServices.objects.create(
            doctor_service=fake.word(),
            department=random.choice(departments),
            price=random.randint(500, 5000),
            discount=round(random.uniform(0, 0.3), 2),
            salary_doctor=random.randint(100, 1000),
            service_label=fake.lexify('????')
        )
        services.append(service)
    return services


def create_payments(doctors, services, n=10):
    payments = []
    for _ in range(n):
        payments.append(Payment.objects.create(
            doctor=random.choice(doctors),
            service=random.choice(services),
            payment_type=random.choice(['cash', 'card'])
        ))
    return payments


def create_patients(doctors, services, departments, receptions, payments, n=10):
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
            appointment_date=date.today(),
            payment=random.choice(payments)
        )
        patients.append(patient)
    return patients


def create_customer_records(patients, receptions, departments, payments, services):
    records = []
    for i, patient in enumerate(patients):
        start_time = time(hour=random.randint(8, 10))
        end_time = (datetime.combine(date.today(), start_time) + timedelta(minutes=30)).time()

        record = CustomerRecord.objects.create(
            reception=random.choice(receptions),
            department=random.choice(departments),
            change=random.randint(0, 100),
            phone_number=patient.phone_number,
            started_time=start_time,
            end_time=end_time,
            payment_type=payments[i % len(payments)],
            doctor_ser=random.choice(services),
            doctor=patient.doctor,
            patient=patient
        )
        records.append(record)
    return records


def create_history_records(patients, receptions, departments, doctors, services, customer_records):
    for i, patient in enumerate(patients):
        HistoryRecord.objects.create(
            patient=patient,
            reception=random.choice(receptions),
            departament=random.choice(departments),
            doctor=random.choice(doctors),
            service=random.choice(services),
            record=random.choice(['был в приеме', 'в ожидании', 'отменен']),
            payment=customer_records[i % len(customer_records)],
            description=fake.sentence()
        )


def create_price_lists(departments, services):
    for _ in range(5):
        PriceList.objects.create(
            department=random.choice(departments),
            service=random.choice(services)
        )


def create_reports(patients):
    for patient in patients:
        if patient.payment:
            Report.objects.create(
                doctor=patient.doctor,
                patient=patient,
                service=patient.doctor_service,
                payment=patient.payment
            )


def run():
    print("Очистка старых данных...")
    Report.objects.all().delete()
    HistoryRecord.objects.all().delete()
    CustomerRecord.objects.all().delete()
    Patient.objects.all().delete()
    Payment.objects.all().delete()
    DoctorServices.objects.all().delete()
    Doctor.objects.all().delete()
    Reception.objects.all().delete()
    Speciality.objects.all().delete()
    Department.objects.all().delete()
    PriceList.objects.all().delete()

    print("Создание данных...")
    departments = create_departments()
    specialities = create_specialities()
    receptions = create_receptions(specialities)
    doctors = create_doctors(departments, specialities)
    services = create_services(departments)
    payments = create_payments(doctors, services)
    patients = create_patients(doctors, services, departments, receptions, payments)
    customer_records = create_customer_records(patients, receptions, departments, payments, services)
    create_history_records(patients, receptions, departments, doctors, services, customer_records)
    create_price_lists(departments, services)
    create_reports(patients)

    print("🎉 Данные успешно засеяны!")


if __name__ == '__main__':
    run()
