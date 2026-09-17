from decimal import Decimal
from django.db import migrations

DEFAULT_LAB_TESTS = [
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

def seed_lab_tests(apps, schema_editor):
    LabTestType = apps.get_model('laboratory', 'LabTestType')
    for t in DEFAULT_LAB_TESTS:
        LabTestType.objects.get_or_create(
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

def unseed_lab_tests(apps, schema_editor):
    LabTestType = apps.get_model('laboratory', 'LabTestType')
    codes = [t['code'] for t in DEFAULT_LAB_TESTS]
    LabTestType.objects.filter(code__in=codes).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('laboratory', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_lab_tests, reverse_code=unseed_lab_tests),
    ]
