from decimal import Decimal
from django.db import migrations

DEFAULT_WARDS = [
    {
        "name": "Médecine Interne",
        "code": "MED",
        "floor": "Rez-de-chaussée",
        "rooms": [
            {"room_number": "MED-01", "room_type": "STANDARD", "daily_rate": 10000, "beds": ["L1", "L2", "L3"]},
            {"room_number": "MED-02", "room_type": "VIP", "daily_rate": 25000, "beds": ["VIP-1", "VIP-2"]},
        ]
    },
    {
        "name": "Maternité",
        "code": "MAT",
        "floor": "1er Étage",
        "rooms": [
            {"room_number": "MAT-01", "room_type": "STANDARD", "daily_rate": 10000, "beds": ["L1", "L2", "L3"]},
            {"room_number": "MAT-02", "room_type": "VIP", "daily_rate": 25000, "beds": ["VIP-1"]},
        ]
    },
    {
        "name": "Pédiatrie",
        "code": "PED",
        "floor": "1er Étage",
        "rooms": [
            {"room_number": "PED-01", "room_type": "STANDARD", "daily_rate": 8000, "beds": ["L1", "L2", "L3", "L4"]},
            {"room_number": "PED-02", "room_type": "VIP", "daily_rate": 20000, "beds": ["VIP-1"]},
        ]
    },
    {
        "name": "Chirurgie",
        "code": "CHR",
        "floor": "2ème Étage",
        "rooms": [
            {"room_number": "CHR-01", "room_type": "STANDARD", "daily_rate": 12000, "beds": ["L1", "L2", "L3"]},
            {"room_number": "CHR-02", "room_type": "ICU", "daily_rate": 35000, "beds": ["ICU-1", "ICU-2"]},
        ]
    },
    {
        "name": "Urgences / Réanimation",
        "code": "URG",
        "floor": "Rez-de-chaussée",
        "rooms": [
            {"room_number": "URG-01", "room_type": "ICU", "daily_rate": 30000, "beds": ["DECHOC-1", "DECHOC-2", "DECHOC-3"]},
            {"room_number": "URG-02", "room_type": "STANDARD", "daily_rate": 10000, "beds": ["L1", "L2", "L3"]},
        ]
    },
]

def seed_wards_and_beds(apps, schema_editor):
    Ward = apps.get_model('rooms', 'Ward')
    Room = apps.get_model('rooms', 'Room')
    Bed = apps.get_model('rooms', 'Bed')

    for w_data in DEFAULT_WARDS:
        ward, _ = Ward.objects.get_or_create(
            code=w_data["code"],
            defaults={
                "name": w_data["name"],
                "floor": w_data["floor"],
                "description": f"Pavillon de {w_data['name']}"
            }
        )
        for r_data in w_data["rooms"]:
            room, _ = Room.objects.get_or_create(
                ward=ward,
                room_number=r_data["room_number"],
                defaults={
                    "room_type": r_data["room_type"],
                    "daily_rate": Decimal(str(r_data["daily_rate"])),
                }
            )
            for bed_num in r_data["beds"]:
                Bed.objects.get_or_create(
                    room=room,
                    bed_number=bed_num,
                    defaults={
                        "status": "AVAILABLE"
                    }
                )

def unseed_wards_and_beds(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_wards_and_beds, reverse_code=unseed_wards_and_beds),
    ]
