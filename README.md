# 🏥 Système de Gestion Hospitalière — Hospital Management System

> Application web de gestion hospitalière multi-rôles, bilingue (FR/EN), conforme aux normes camerounaises (Mobile Money, FCFA, fuseau horaire Africa/Douala).

## Stack Technique
- Django 5.2 LTS + PostgreSQL + Redis + Celery
- WeasyPrint (PDF), Django REST Framework (API)
- Orange Money + MTN MoMo (paiement mobile)
- django-otp (2FA), django-simple-history (audit)
- Docker Compose (prod-ready)

## Démarrage rapide

```bash
# 1. Environnement virtuel
python -m venv .venv && .venv\Scripts\activate

# 2. Dépendances
pip install -r requirements/dev.txt

# 3. Variables d env
copy .env.example .env   # puis editer .env

# 4. Base de données (SQLite pour dev)
python manage.py migrate
python manage.py compilemessages
python manage.py createsuperuser

# 5. Serveur
python manage.py runserver
# -> http://127.0.0.1:8000
```

## Docker Compose
```bash
docker compose up --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## Modules
- Patients (DPI/EHR), Rendez-vous + File d'attente HTMX
- Consultations, Ordonnances, Constantes vitales
- Pharmacie (stocks, alertes Celery Beat)
- Laboratoire (analyses, PDF rapports)
- Rooms & Hospitalisation (matrice lits)
- Caisse & Facturation (Mobile Money Orange/MTN)
- API REST (DRF), Notifications SMS, 2FA TOTP

## Roles
Admin, Médecin, Infirmier, Réceptionniste, Pharmacien, Laborantin, Caissier

## Tests
```bash
pytest
pytest --cov=apps --cov-report=html
```

## i18n
Francais (par defaut) + Anglais. Selecteur de langue dans la navbar.
```bash
python manage.py makemessages -l fr -l en
python manage.py compilemessages
```

## Production
Voir .env.example pour la configuration complete.
DEBUG=False, HTTPS, HSTS, SECRET_KEY fort requis.
