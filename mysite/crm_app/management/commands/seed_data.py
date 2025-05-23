from django.core.management.base import BaseCommand
from django.utils import timezone
from crm_app.models import (
    Department, Speciality, Reception, Doctor, DoctorServices,
    Patient, Payment, CustomerRecord, HistoryRecord,
    PriceList, Analytics
)
from faker import Faker
import random

fake = Faker('ru_RU')

class Command(BaseCommand):
    help = "Seed database with test data for all CRM models"

    def handle(self, *args, **kwargs):
        self.stdout.write("🧹 Очистка таблиц...")
        # Чистим таблицы (осторожно, в реальных проектах так делать нельзя)
        models = [Analytics, PriceList, HistoryRecord, CustomerRecord, Payment, Patient, DoctorServices, Doctor, Reception, Speciality, Department]
        for model in models:
            model.objects.all().delete()

        self.stdout.write("🌱 Создаем Departments...")
        departments = []
        for dep_name in ['Терапия', 'Кардиология', 'Неврология']:
            d = Department.objects.create(department_name=dep_name)
            departments.append(d)

        self.stdout.write("🌿 Создаем Specialities...")
        specialities = []
        for spec_title in ['Кардиолог', 'Терапевт', 'Невролог']:
            s = Speciality.objects.create(speciality_title=spec_title)
            specialities.append(s)

        self.stdout.write("👩‍⚕️ Создаем Reception и Doctor...")
        receptions = []
        for _ in range(2):
            rec = Reception.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                speciality=random.choice(specialities),
            )
            receptions.append(rec)

        doctors = []
        for _ in range(3):
            doc = Doctor.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                speciality=random.choice(specialities),
                department=random.choice(departments),
                medical_license=fake.bothify(text='???-####'),
                cabinet=str(random.randint(1, 30)),
            )
            doctors.append(doc)

        self.stdout.write("🛠 Создаем DoctorServices...")
        services = []
        for i in range(5):
            serv = DoctorServices.objects.create(
                doctor_service=fake.job(),
                department=random.choice(departments),
                price=random.randint(1000, 5000),
                discount=random.choice([0.0, 0.1, 0.15]),
                salary_doctor=random.randint(500, 1500),
            )
            services.append(serv)

        self.stdout.write("👨‍👩‍👧 Создаем Patients...")
        patients = []
        genders = ['Мужской', 'Женский']
        status_choices = ['Живая очередь', 'Предзапись', 'Отмененные']
        for _ in range(10):
            patient = Patient.objects.create(
                full_name=fake.name(),
                phone_number=fake.phone_number(),
                doctor_service=random.choice(services),
                birthday=fake.date_of_birth(minimum_age=18, maximum_age=90),
                department=random.choice(departments),
                reception=random.choice(receptions),
                started_time=fake.time(),
                end_time=fake.time(),
                gender_patient=random.choice(genders),
                doctor=random.choice(doctors),
                status_patient=random.choice(status_choices),
            )
            patients.append(patient)

        self.stdout.write("💳 Создаем Payments...")
        payments = []
        payment_types = ['cash', 'card']
        for p in patients:
            pay = Payment.objects.create(
                patient=p,
                doctor=p.doctor,
                service=p.doctor_service,
                payment_type=random.choice(payment_types),
            )
            payments.append(pay)

        self.stdout.write("🧾 Создаем CustomerRecords...")
        customer_records = []
        for p, pay in zip(patients, payments):
            cr = CustomerRecord.objects.create(
                reception=p.reception,
                department=p.department,
                change=random.randint(0, 1000),
                phone_number=p.phone_number,
                payment_type=pay,
            )
            customer_records.append(cr)

        self.stdout.write("📜 Создаем HistoryRecords...")
        for i in range(10):
            HistoryRecord.objects.create(
                patient=random.choice(patients),
                reception=random.choice(receptions),
                departament=random.choice(departments),
                doctor=random.choice(doctors),
                service=random.choice(services),
                record=random.choice(['был в приеме', 'в ожидании', 'отменен']),
                payment=random.choice(customer_records),
                description=fake.text(max_nb_chars=100),
            )

        self.stdout.write("💰 Создаем PriceList...")
        for dep in departments:
            for serv in services:
                PriceList.objects.create(
                    department=dep,
                    service=serv,
                )

        self.stdout.write("📊 Создаем Analytics...")
        for _ in range(5):
            Analytics.objects.create(
                date=fake.date_this_year(),
                patient=random.choice(patients),
                service=random.choice(services),
            )

        self.stdout.write(self.style.SUCCESS("✅ Все данные успешно добавлены!"))
