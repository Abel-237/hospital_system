"""
Management command: create_demo_data
Populates the database with a realistic set of demo data for development
and demonstration purposes.

Usage:
    python manage.py create_demo_data [--flush]

Options:
    --flush    Delete all existing application data before seeding (admin users are preserved).
"""
import random
from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


# ─── Seed data pools ────────────────────────────────────────────────────────

STAFF = [
    {"username": "dr_mbarga",   "first_name": "Jean-Paul",   "last_name": "Mbarga",   "role": "DOCTOR",       "speciality": "Médecine Générale",   "license_number": "CMO-2021-4521"},
    {"username": "dr_biyong",   "first_name": "Christelle",  "last_name": "Biyong",   "role": "DOCTOR",       "speciality": "Pédiatrie",           "license_number": "CMO-2019-3302"},
    {"username": "inf_tchoua",  "first_name": "Martine",     "last_name": "Tchoua",   "role": "NURSE",        "speciality": "Soins infirmiers",    "license_number": ""},
    {"username": "pharma_nkoa", "first_name": "Samuel",      "last_name": "Nkoa",     "role": "PHARMACIST",   "speciality": "Pharmacologie",       "license_number": "CNP-2020-7734"},
    {"username": "lab_essono",  "first_name": "Brigitte",    "last_name": "Essono",   "role": "LABORANT",     "speciality": "Biologie Médicale",   "license_number": ""},
    {"username": "caisse_fono", "first_name": "André",       "last_name": "Fono",     "role": "CASHIER",      "speciality": "",                    "license_number": ""},
    {"username": "accueil_abi", "first_name": "Patience",    "last_name": "Abiodun",  "role": "RECEPTIONIST", "speciality": "",                    "license_number": ""},
    {"username": "admin_hosp",  "first_name": "Administrateur", "last_name": "Système", "role": "ADMIN",     "speciality": "Administration",      "license_number": ""},
]

PATIENT_DATA = [
    {"first_name": "Alain",      "last_name": "Fotso",       "gender": "M", "birth_date": "1985-04-12", "blood_group": "O+",  "phone": "+237671234561", "city": "Douala"},
    {"first_name": "Marie",      "last_name": "Ngono",        "gender": "F", "birth_date": "1992-07-03", "blood_group": "A+",  "phone": "+237691234562", "city": "Yaoundé"},
    {"first_name": "Pierre",     "last_name": "Ateba",        "gender": "M", "birth_date": "1978-11-25", "blood_group": "B+",  "phone": "+237670234563", "city": "Douala"},
    {"first_name": "Sophie",     "last_name": "Mba",          "gender": "F", "birth_date": "2000-02-14", "blood_group": "AB+", "phone": "+237655234564", "city": "Bafoussam"},
    {"first_name": "Joseph",     "last_name": "Bello",        "gender": "M", "birth_date": "1965-08-30", "blood_group": "O-",  "phone": "+237681234565", "city": "Douala"},
    {"first_name": "Hortense",   "last_name": "Ekwalla",      "gender": "F", "birth_date": "1990-01-19", "blood_group": "A-",  "phone": "+237671234566", "city": "Douala"},
    {"first_name": "Emmanuel",   "last_name": "Ndjana",       "gender": "M", "birth_date": "1972-05-08", "blood_group": "B-",  "phone": "+237691234567", "city": "Yaoundé"},
    {"first_name": "Cecile",     "last_name": "Ombaga",       "gender": "F", "birth_date": "2005-09-22", "blood_group": "O+",  "phone": "+237656234568", "city": "Ngaoundéré"},
    {"first_name": "Blaise",     "last_name": "Onana",        "gender": "M", "birth_date": "1988-12-01", "blood_group": "A+",  "phone": "+237670134569", "city": "Douala"},
    {"first_name": "Adeline",    "last_name": "Mbock",        "gender": "F", "birth_date": "1975-06-17", "blood_group": "AB-", "phone": "+237691034570", "city": "Kribi"},
    {"first_name": "Augustin",   "last_name": "Tebou",        "gender": "M", "birth_date": "1995-03-25", "blood_group": "O+",  "phone": "+237678234571", "city": "Bafoussam"},
    {"first_name": "Claudine",   "last_name": "Mveng",        "gender": "F", "birth_date": "1983-10-11", "blood_group": "A+",  "phone": "+237698234572", "city": "Douala"},
]

MEDICATIONS = [
    {"name": "Amoxicilline",   "dci": "amoxicillin",        "form": "TABLET",     "dosage": "500mg",    "unit_price": 350,  "threshold": 20},
    {"name": "Paracétamol",    "dci": "paracetamol",        "form": "TABLET",     "dosage": "1g",       "unit_price": 150,  "threshold": 50},
    {"name": "Ibuprofen",      "dci": "ibuprofen",          "form": "TABLET",     "dosage": "400mg",    "unit_price": 250,  "threshold": 30},
    {"name": "Cotrimoxazole",  "dci": "cotrimoxazole",      "form": "TABLET",     "dosage": "480mg",    "unit_price": 200,  "threshold": 25},
    {"name": "Metronidazole",  "dci": "metronidazole",      "form": "TABLET",     "dosage": "500mg",    "unit_price": 300,  "threshold": 20},
    {"name": "Artéméther-Luméfantrine", "dci": "AL",         "form": "TABLET",    "dosage": "20/120mg", "unit_price": 800,  "threshold": 30},
    {"name": "Amlodipine",     "dci": "amlodipine",         "form": "TABLET",     "dosage": "5mg",      "unit_price": 500,  "threshold": 15},
    {"name": "Metformine",     "dci": "metformin",          "form": "TABLET",     "dosage": "500mg",    "unit_price": 450,  "threshold": 20},
    {"name": "Oméprazole",     "dci": "omeprazole",         "form": "TABLET",     "dosage": "20mg",     "unit_price": 600,  "threshold": 20},
    {"name": "Céftriaxone",    "dci": "ceftriaxone",        "form": "INJECTABLE", "dosage": "1g",       "unit_price": 2500, "threshold": 10},
    {"name": "NaCl 0.9%",      "dci": "saline solution",    "form": "INJECTABLE", "dosage": "500ml",    "unit_price": 1200, "threshold": 15},
    {"name": "Amoxicilline Sirop", "dci": "amoxicillin",    "form": "SYRUP",     "dosage": "250mg/5ml", "unit_price": 1800, "threshold": 10},
    {"name": "Ciprofloxacine", "dci": "ciprofloxacin",      "form": "TABLET",     "dosage": "500mg",    "unit_price": 700,  "threshold": 15},
    {"name": "Furosémide",     "dci": "furosemide",         "form": "TABLET",     "dosage": "40mg",     "unit_price": 200,  "threshold": 20},
    {"name": "Atenolol",       "dci": "atenolol",           "form": "TABLET",     "dosage": "50mg",     "unit_price": 350,  "threshold": 15},
]

LAB_TESTS = [
    {"name": "Numération Formule Sanguine (NFS)", "code": "NFS",    "category": "HEMATOLOGY",   "price": 5000,  "unit": "x10³/µL",     "normal_min": "4.5",  "normal_max": "11"},
    {"name": "Groupe Sanguin + Rhésus",           "code": "GSBR",   "category": "HEMATOLOGY",   "price": 3500,  "unit": "",            "normal_min": "",     "normal_max": ""},
    {"name": "Vitesse de Sédimentation (VS)",     "code": "VS",     "category": "HEMATOLOGY",   "price": 2000,  "unit": "mm/h",        "normal_min": "0",    "normal_max": "15"},
    {"name": "Glycémie à Jeun",                   "code": "GLUC",   "category": "BIOCHEMISTRY", "price": 3000,  "unit": "g/L",         "normal_min": "0.70", "normal_max": "1.10"},
    {"name": "Créatininémie",                     "code": "CREAT",  "category": "BIOCHEMISTRY", "price": 4000,  "unit": "mg/L",        "normal_min": "7",    "normal_max": "13"},
    {"name": "Uricémie (Acide Urique)",           "code": "URIC",   "category": "BIOCHEMISTRY", "price": 4000,  "unit": "mg/L",        "normal_min": "30",   "normal_max": "70"},
    {"name": "Cholestérol Total",                 "code": "CHOL",   "category": "BIOCHEMISTRY", "price": 4500,  "unit": "g/L",         "normal_min": "",     "normal_max": "2.0"},
    {"name": "Sérologie VIH 1&2",                 "code": "VIH",    "category": "SEROLOGY",     "price": 6000,  "unit": "",            "normal_min": "",     "normal_max": "Négatif"},
    {"name": "Antigène HBs (Hépatite B)",         "code": "HBSAG",  "category": "SEROLOGY",     "price": 5500,  "unit": "",            "normal_min": "",     "normal_max": "Négatif"},
    {"name": "Test de Grossesse β-HCG",           "code": "BHCG",   "category": "SEROLOGY",     "price": 4000,  "unit": "mUI/mL",      "normal_min": "",     "normal_max": "5"},
    {"name": "Goutte Épaisse (Paludisme)",         "code": "PALU",   "category": "PARASITOLOGY", "price": 3500,  "unit": "",            "normal_min": "",     "normal_max": "Négatif"},
    {"name": "Examen Direct des Selles (EPS)",    "code": "EPS",    "category": "PARASITOLOGY", "price": 3000,  "unit": "",            "normal_min": "",     "normal_max": "Négatif"},
    {"name": "ECBU (Examen Cytobactériologique)", "code": "ECBU",   "category": "MICROBIOLOGY", "price": 5500,  "unit": "",            "normal_min": "",     "normal_max": "Stérile"},
    {"name": "Radiographie Pulmonaire F+P",       "code": "RXPULM", "category": "IMAGING",      "price": 15000, "unit": "",            "normal_min": "",     "normal_max": "Normal"},
    {"name": "Échographie Abdominale",            "code": "ECHABO", "category": "IMAGING",      "price": 20000, "unit": "",            "normal_min": "",     "normal_max": "Normal"},
]

WARDS = [
    {"name": "Médecine Interne",    "code": "MED", "floor": "Rez-de-chaussée"},
    {"name": "Maternité",           "code": "MAT", "floor": "1er Étage"},
    {"name": "Pédiatrie",           "code": "PED", "floor": "1er Étage"},
    {"name": "Chirurgie",           "code": "CHR", "floor": "2ème Étage"},
    {"name": "Urgences / Réanimation", "code": "URG", "floor": "Rez-de-chaussée"},
]


class Command(BaseCommand):
    help = "Seed the database with realistic Cameroonian hospital demo data."

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Flush all existing app data before seeding.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write(self.style.WARNING("⚠  Flushing existing data..."))
            self._flush_data()

        self.stdout.write(self.style.MIGRATE_HEADING("🏥 Seeding Hospital Demo Data..."))

        staff_map = self._create_staff()
        patients = self._create_patients()
        medications = self._create_medications()
        lab_tests = self._create_lab_tests()
        wards, beds = self._create_ward_structure()
        self._create_appointments(patients, staff_map)
        self._create_consultations_and_prescriptions(patients, staff_map)
        self._create_lab_orders(patients, staff_map, lab_tests)
        self._create_admissions(patients, staff_map, beds)
        self._create_invoices(patients, staff_map)

        self.stdout.write(self.style.SUCCESS(
            "\n✅ Demo data created successfully!\n"
            "   Login credentials for all demo staff: password = Demo@2026!\n"
            "   → Admin:       admin_hosp / Demo@2026!\n"
            "   → Médecin:     dr_mbarga  / Demo@2026!\n"
            "   → Infirmière:  inf_tchoua / Demo@2026!\n"
            "   → Pharmacien:  pharma_nkoa / Demo@2026!\n"
            "   → Laborantin:  lab_essono  / Demo@2026!\n"
            "   → Caissier:    caisse_fono / Demo@2026!\n"
        ))

    # ── Private helpers ────────────────────────────────────────────────────

    def _flush_data(self):
        """Delete all business data but preserve superusers."""
        from apps.billing.models import Payment, InvoiceItem, Invoice, InsurancePolicy
        from apps.pharmacy.models import DispensationItem, Dispensation, StockBatch, Medication
        from apps.laboratory.models import LabOrderItem, LabOrder, LabTestType
        from apps.rooms.models import NursingNote, Admission, Bed, Room, Ward
        from apps.consultations.models import PrescriptionItem, Prescription, VitalSigns, Consultation
        from apps.appointments.models import Appointment
        from apps.patients.models import Patient
        from apps.notifications.models import NotificationLog

        for Model in [
            Payment, InvoiceItem, Invoice, InsurancePolicy,
            DispensationItem, Dispensation, StockBatch, Medication,
            LabOrderItem, LabOrder, LabTestType,
            NursingNote, Admission, Bed, Room, Ward,
            PrescriptionItem, Prescription, VitalSigns, Consultation,
            Appointment, Patient, NotificationLog,
        ]:
            Model.objects.all().delete()
        # Remove demo staff only (keep superusers)
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write("  Data flushed.")

    def _create_staff(self):
        """Create hospital staff users."""
        self.stdout.write("  👤 Creating staff users...")
        staff_map = {}
        for s in STAFF:
            user, created = User.objects.get_or_create(
                username=s['username'],
                defaults={
                    'first_name': s['first_name'],
                    'last_name': s['last_name'],
                    'role': s['role'],
                    'speciality': s['speciality'],
                    'license_number': s['license_number'],
                    'phone_number': f"+2376{random.randint(10000000,99999999)}",
                    'email': f"{s['username']}@hopital-cmr.local",
                    'is_active': True,
                }
            )
            if created:
                user.set_password("Demo@2026!")
                user.save()
            staff_map[s['role']] = staff_map.get(s['role'], []) + [user]
            self.stdout.write(f"    {'[CREATED]' if created else '[EXISTS] '} {user.display_title} ({user.role})")
        return staff_map

    def _create_patients(self):
        """Create demo patients."""
        from apps.patients.models import Patient
        self.stdout.write("  🧍 Creating patients...")
        patients = []
        for p in PATIENT_DATA:
            patient, _ = Patient.objects.get_or_create(
                phone=p['phone'],
                defaults={
                    'first_name': p['first_name'],
                    'last_name': p['last_name'],
                    'gender': p['gender'],
                    'birth_date': date.fromisoformat(p['birth_date']),
                    'blood_group': p['blood_group'],
                    'city': p['city'],
                    'address': f"Quartier {random.choice(['Akwa','Bonanjo','Bassa','Cité Verte','Ngousso'])}, {p['city']}",
                    'allergies': random.choice(['', 'Pénicilline', 'Aspirine', 'Latex', '']),
                    'chronic_conditions': random.choice(['', 'Hypertension artérielle', 'Diabète type 2', 'Asthme bronchique', '']),
                    'consent_given': True,
                    'consent_given_at': timezone.now(),
                }
            )
            patients.append(patient)
        self.stdout.write(f"    {len(patients)} patients loaded.")
        return patients

    def _create_medications(self):
        """Create drug formulary."""
        from apps.pharmacy.models import Medication, StockBatch
        self.stdout.write("  💊 Creating medications & stock batches...")
        meds = []
        today = timezone.now().date()
        for m in MEDICATIONS:
            med, _ = Medication.objects.get_or_create(
                name=m['name'],
                defaults={
                    'dci': m['dci'],
                    'form': m['form'],
                    'dosage': m['dosage'],
                    'unit_price': Decimal(str(m['unit_price'])),
                    'critical_stock_threshold': m['threshold'],
                    'is_active': True,
                }
            )
            # Add 2 stock batches per medication
            for i, (qty, months) in enumerate([(random.randint(50, 200), 18), (random.randint(10, 50), 6)]):
                batch_num = f"LOT-{med.name[:3].upper()}-2026-0{i+1}"
                StockBatch.objects.get_or_create(
                    medication=med,
                    batch_number=batch_num,
                    defaults={
                        'expiration_date': today + timedelta(days=30 * months),
                        'quantity': qty,
                        'purchase_price': Decimal(str(m['unit_price'])) * Decimal('0.6'),
                        'received_date': today - timedelta(days=random.randint(10, 60)),
                    }
                )
            meds.append(med)
        self.stdout.write(f"    {len(meds)} medications with stock batches.")
        return meds

    def _create_lab_tests(self):
        """Create laboratory test catalog."""
        from apps.laboratory.models import LabTestType
        self.stdout.write("  🔬 Creating lab test catalog...")
        tests = []
        for t in LAB_TESTS:
            test, _ = LabTestType.objects.get_or_create(
                code=t['code'],
                defaults={
                    'name': t['name'],
                    'category': t['category'],
                    'price': Decimal(str(t['price'])),
                    'unit': t['unit'],
                    'normal_range_min': t['normal_min'],
                    'normal_range_max': t['normal_max'],
                    'is_active': True,
                }
            )
            tests.append(test)
        self.stdout.write(f"    {len(tests)} lab test types loaded.")
        return tests

    def _create_ward_structure(self):
        """Create hospital wards, rooms, and beds."""
        from apps.rooms.models import Ward, Room, Bed
        self.stdout.write("  🛏  Creating ward/room/bed structure...")
        beds_all = []
        for w in WARDS:
            ward, _ = Ward.objects.get_or_create(code=w['code'], defaults={'name': w['name'], 'floor': w['floor']})
            # 3 rooms per ward, 4 beds per room
            for r_num in range(1, 4):
                room, _ = Room.objects.get_or_create(
                    ward=ward,
                    room_number=f"{w['code']}-{r_num:02d}",
                    defaults={
                        'room_type': random.choice(['STANDARD', 'STANDARD', 'VIP']),
                        'daily_rate': Decimal(random.choice(['10000', '25000', '50000'])),
                    }
                )
                for b_num in range(1, 5):
                    bed, _ = Bed.objects.get_or_create(
                        room=room,
                        bed_number=f"L{b_num}",
                        defaults={'status': Bed.Status.AVAILABLE}
                    )
                    beds_all.append(bed)
        self.stdout.write(f"    {Bed.objects.count()} beds across {Ward.objects.count()} wards.")
        return Ward.objects.all(), beds_all

    def _create_appointments(self, patients, staff_map):
        """Create today's appointment queue and historical ones."""
        from apps.appointments.models import Appointment
        self.stdout.write("  📅 Creating appointments...")
        doctors = staff_map.get('DOCTOR', [])
        if not doctors:
            return
        today = timezone.now().date()
        statuses = ['WAITING', 'IN_CONSULTATION', 'COMPLETED', 'SCHEDULED', 'COMPLETED']
        created_count = 0
        for i, patient in enumerate(patients[:8]):
            doctor = doctors[i % len(doctors)]
            apt_time = time(8 + i, 0)
            # Check the unique constraint first
            if not Appointment.objects.filter(doctor=doctor, scheduled_date=today, scheduled_time=apt_time).exists():
                apt = Appointment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    scheduled_date=today,
                    scheduled_time=apt_time,
                    reason=random.choice([
                        "Fièvre et céphalées",
                        "Contrôle hypertension",
                        "Douleurs abdominales",
                        "Toux persistante",
                        "Renouvellement ordonnance",
                        "Visite de routine",
                        "Douleurs articulaires",
                        "Examen prénatal"
                    ]),
                    priority='NORMAL',
                    status=statuses[i % len(statuses)],
                    queue_number=i + 1 if statuses[i % len(statuses)] in ['WAITING', 'IN_CONSULTATION', 'COMPLETED'] else None,
                    arrival_time=timezone.now() - timedelta(minutes=random.randint(5, 120)) if statuses[i % len(statuses)] != 'SCHEDULED' else None,
                )
                created_count += 1
        self.stdout.write(f"    {created_count} appointments for today.")

    def _create_consultations_and_prescriptions(self, patients, staff_map):
        """Create past consultations with prescriptions."""
        from apps.consultations.models import Consultation, VitalSigns, Prescription, PrescriptionItem
        self.stdout.write("  🩺 Creating consultations & prescriptions...")
        doctors = staff_map.get('DOCTOR', [])
        nurses = staff_map.get('NURSE', [staff_map.get('DOCTOR', [None])[0]])
        if not doctors:
            return
        diagnoses = [
            ("Paludisme simple", "Artéméther-Luméfantrine", "2 comprimés deux fois/jour", "3 jours", 6),
            ("Hypertension artérielle", "Amlodipine", "1 comprimé par jour", "30 jours", 30),
            ("Diabète type 2 non contrôlé", "Metformine", "1 comprimé matin et soir", "30 jours", 60),
            ("Infection respiratoire haute", "Amoxicilline", "1 gélule matin midi soir", "7 jours", 21),
            ("Gastro-entérite aiguë", "Paracétamol", "1 comprimé 3x/jour si douleur", "5 jours", 15),
            ("Infection urinaire", "Ciprofloxacine", "1 comprimé matin et soir", "7 jours", 14),
        ]
        count = 0
        for i, patient in enumerate(patients):
            diag = diagnoses[i % len(diagnoses)]
            doctor = doctors[i % len(doctors)]
            nurse = nurses[0] if nurses else doctor

            # Vitals recorded by nurse
            vitals = VitalSigns.objects.create(
                patient=patient,
                recorded_by=nurse,
                temperature=Decimal(str(round(random.uniform(36.5, 39.2), 1))),
                blood_pressure_systolic=random.randint(100, 155),
                blood_pressure_diastolic=random.randint(60, 100),
                pulse_rate=random.randint(60, 105),
                respiratory_rate=random.randint(14, 22),
                oxygen_saturation=Decimal(str(round(random.uniform(95.0, 99.5), 1))),
                weight=Decimal(str(round(random.uniform(45, 95), 1))),
                height=Decimal(str(round(random.uniform(155, 185), 1))),
            )

            consultation = Consultation.objects.create(
                patient=patient,
                doctor=doctor,
                vital_signs=vitals,
                symptoms=f"Plainte principale: {diag[0].lower()}. Patient se plaint de malaise général.",
                physical_examination="Examen général: conscient, orienté. Auscultation cardio-pulmonaire normale.",
                diagnosis=diag[0],
                clinical_notes="Patient informé du diagnostic. Traitement prescrit. Revoir dans 7 jours si persistance.",
            )

            prescription = Prescription.objects.create(
                consultation=consultation,
                patient=patient,
                doctor=doctor,
                notes="Prendre les médicaments avec les repas. Éviter l'alcool."
            )
            PrescriptionItem.objects.create(
                prescription=prescription,
                medication_name=diag[1],
                dosage=diag[2],
                duration=diag[3],
                quantity=diag[4],
                instructions="À prendre avec de l'eau."
            )
            count += 1
        self.stdout.write(f"    {count} consultations with prescriptions.")

    def _create_lab_orders(self, patients, staff_map, lab_tests):
        """Create lab orders with some results."""
        from apps.laboratory.models import LabOrder, LabOrderItem
        self.stdout.write("  🔬 Creating lab orders...")
        doctors = staff_map.get('DOCTOR', [])
        laborants = staff_map.get('LABORANT', [])
        if not doctors or not lab_tests:
            return
        count = 0
        for i, patient in enumerate(patients[:8]):
            doctor = doctors[i % len(doctors)]
            selected_tests = random.sample(lab_tests, min(3, len(lab_tests)))
            order = LabOrder.objects.create(
                patient=patient,
                prescribed_by=doctor,
                status=random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED', 'COMPLETED']),
                priority=random.choice(['NORMAL', 'NORMAL', 'URGENT']),
                clinical_indications=f"Bilan de contrôle suite à consultation pour {patient.full_name}.",
            )
            for test in selected_tests:
                item = LabOrderItem.objects.create(
                    order=order,
                    test_type=test,
                )
                if order.status == 'COMPLETED' and laborants:
                    item.result_value = f"{random.uniform(0.5, 10.0):.2f}" if test.unit else "Négatif"
                    item.is_abnormal = random.random() < 0.2
                    item.analyzed_by = laborants[0]
                    item.analyzed_at = timezone.now() - timedelta(hours=random.randint(1, 6))
                    item.save()
            if order.status == 'COMPLETED':
                order.completed_at = timezone.now() - timedelta(hours=random.randint(1, 4))
                order.save()
            count += 1
        self.stdout.write(f"    {count} lab orders with results.")

    def _create_admissions(self, patients, staff_map, beds):
        """Create hospital admissions (inpatients)."""
        from apps.rooms.models import Admission, Bed
        self.stdout.write("  🛏  Creating active admissions...")
        doctors = staff_map.get('DOCTOR', [])
        if not doctors or not beds:
            return
        available_beds = [b for b in beds if b.status == Bed.Status.AVAILABLE]
        count = 0
        for i, patient in enumerate(patients[:4]):
            if i >= len(available_beds):
                break
            bed = available_beds[i]
            doctor = doctors[i % len(doctors)]
            Admission.objects.create(
                patient=patient,
                bed=bed,
                admitting_doctor=doctor,
                admission_date=timezone.now() - timedelta(days=random.randint(1, 5)),
                admission_reason=random.choice([
                    "Paludisme sévère avec anémie profonde",
                    "Hypertension artérielle non contrôlée",
                    "Décompensation diabétique - ACD",
                    "Pneumopathie aiguë communautaire"
                ]),
            )
            bed.status = Bed.Status.OCCUPIED
            bed.save()
            count += 1
        self.stdout.write(f"    {count} active admissions.")

    def _create_invoices(self, patients, staff_map):
        """Create invoices with mixed payment statuses."""
        from apps.billing.models import Invoice, InvoiceItem, Payment
        self.stdout.write("  💰 Creating invoices & payments...")
        cashiers = staff_map.get('CASHIER', [])
        if not cashiers:
            return
        cashier = cashiers[0]
        statuses_config = [
            ('PAID', Payment.Method.CASH, Payment.Status.SUCCESS),
            ('PAID', Payment.Method.ORANGE_MONEY, Payment.Status.SUCCESS),
            ('PAID', Payment.Method.MTN_MOMO, Payment.Status.SUCCESS),
            ('PARTIALLY_PAID', Payment.Method.CASH, Payment.Status.SUCCESS),
            ('PENDING', None, None),
            ('PENDING', None, None),
        ]
        count = 0
        for i, patient in enumerate(patients[:6]):
            cfg = statuses_config[i]
            invoice_status, pay_method, pay_status = cfg

            invoice = Invoice.objects.create(
                patient=patient,
                status='PENDING',
            )
            items_data = [
                ("Consultation médicale générale", "CONSULTATION", 1, Decimal('5000')),
                ("Examens de laboratoire (NFS, Glycémie)", "LABORATORY", 1, Decimal('8000')),
                ("Médicaments prescrits", "PHARMACY", 1, Decimal(str(random.randint(3000, 15000)))),
            ]
            for desc, cat, qty, price in items_data:
                InvoiceItem.objects.create(invoice=invoice, description=desc, category=cat, quantity=qty, unit_price=price)

            invoice.recalculate_totals()

            if pay_method and pay_status:
                amount = invoice.patient_net_amount if invoice_status == 'PAID' else invoice.patient_net_amount * Decimal('0.5')
                Payment.objects.create(
                    invoice=invoice,
                    method=pay_method,
                    amount=amount,
                    payer_phone=patient.phone,
                    status=pay_status,
                    received_by=cashier,
                )
                invoice.paid_amount = amount
                invoice.recalculate_totals()
            count += 1
        self.stdout.write(f"    {count} invoices (paid + pending).")
