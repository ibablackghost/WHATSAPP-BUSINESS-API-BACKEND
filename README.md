# WhatBot Pro — Backend API

Plateforme SaaS africaine de service client automatisé sur **WhatsApp Business Cloud API**.

## Stack

| Composant | Technologie |
|-----------|-------------|
| Backend | Python 3.12, Django 5, DRF |
| Base de données | PostgreSQL 15+ avec pgvector |
| Cache / Queue | Redis, Celery, Celery Beat |
| Temps réel | Django Channels, WebSockets |
| Auth | JWT + 2FA TOTP |
| IA | OpenAI GPT-4o, embeddings RAG |
| Paiements | Wave, Orange Money, Free Money |
| Infra | Docker, Nginx, AWS S3 |

## Architecture

```
whatbot_pro/
├── whatbot_pro/          # Configuration Django
├── apps/
│   ├── core/             # Multi-tenancy, audit, events
│   ├── organizations/    # Tenants
│   ├── accounts/         # Auth JWT + 2FA
│   ├── contacts/         # Contacts WhatsApp
│   ├── whatsapp/         # Cloud API, webhooks
│   ├── conversations/    # Live chat
│   ├── bots/             # Flow engine USSD
│   ├── agents/           # Agents, round-robin
│   ├── ai/               # RAG, embeddings
│   ├── payments/         # Mobile Money
│   ├── notifications/    # Campagnes
│   └── analytics/        # KPIs, exports
```

Chaque app suit : `models/`, `services/`, `repositories/`, `api/`, `tasks/`, `tests/`.

## Démarrage rapide (Docker)

```bash
cd whatbot_pro
cp .env.example .env
# Éditer .env avec vos clés Meta / OpenAI

docker compose up -d db redis
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py seed_data
docker compose up
```

- API : http://localhost:8000
- Docs OpenAPI : http://localhost:8000/api/docs/
- Health : http://localhost:8000/health/

## Démarrage local (sans Docker)

```bash
cd whatbot_pro
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# PostgreSQL avec extension vector
createdb whatbot_pro
psql whatbot_pro -c "CREATE EXTENSION IF NOT EXISTS vector;"

cp .env.example .env
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Celery (terminal séparé) :
```bash
celery -A whatbot_pro worker -l info -Q default,whatsapp,payments,notifications,ai
celery -A whatbot_pro beat -l info
```

## Configuration WhatsApp Business API

1. Créer une app sur [Meta for Developers](https://developers.facebook.com/)
2. Configurer WhatsApp Business Cloud API
3. Renseigner dans `.env` :
   ```
   WHATSAPP_VERIFY_TOKEN=votre-token-verification
   WHATSAPP_APP_SECRET=votre-app-secret
   ```
4. Configurer le webhook Meta :
   - URL : `https://votre-domaine.com/api/v1/whatsapp/webhook/`
   - Verify token : identique à `WHATSAPP_VERIFY_TOKEN`
   - Champs : `messages`, `message_template_status_update`
5. Via API, configurer les credentials organisation :
   ```http
   POST /api/v1/organizations/whatsapp-config/
   Authorization: Bearer <token>
   X-Organization-ID: <org-uuid>
   {
     "phone_number_id": "VOTRE_PHONE_NUMBER_ID",
     "business_account_id": "VOTRE_WABA_ID",
     "access_token": "VOTRE_TOKEN_PERMANENT"
   }
   ```

## API principale

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/register/` | Inscription |
| `POST /api/v1/auth/login/` | Connexion JWT |
| `POST /api/v1/auth/2fa/setup/` | Activer 2FA |
| `GET /api/v1/organizations/current/` | Organisation courante |
| `POST /api/v1/whatsapp/webhook/` | Webhook Meta |
| `POST /api/v1/whatsapp/send/` | Envoyer un message |
| `GET /api/v1/conversations/` | Conversations live chat |
| `GET /api/v1/bots/flows/` | Flows conversationnels |
| `POST /api/v1/ai/chat/` | Chat IA avec RAG |
| `POST /api/v1/payments/initiate/` | Paiement Mobile Money |
| `GET /api/v1/analytics/dashboard/` | KPIs temps réel |

**Header obligatoire** : `X-Organization-ID: <uuid>` sur toutes les requêtes authentifiées.

## WebSockets

| URL | Événements |
|-----|------------|
| `ws/conversations/<id>/` | `new_message`, `assigned`, `typing`, `payment_confirmed` |
| `ws/agents/` | `online_status` |
| `ws/notifications/` | `campaign_update` |

## Flow Engine

Types de nœuds : `message`, `menu`, `condition`, `api_call`, `ai`, `payment`, `assign_agent`, `end`.

Variables de contexte dans `SessionState.context_variables`. Timeout configurable par flow.

## Tests

```bash
pytest
pytest --cov=apps --cov-report=term-missing
```

## Compte démo (seed)

- Email : `admin@whatbot.pro`
- Mot de passe : `Admin@WhatBot2024!`
- Organisation : `demo`

## Sécurité

- JWT avec rotation refresh tokens
- 2FA TOTP (pyotp)
- Validation signature webhook Meta (HMAC SHA-256)
- Chiffrement AES des tokens WhatsApp (Fernet)
- Rate limiting DRF
- Audit logs
- RGPD : `POST /api/v1/auth/gdpr/delete-request/`

## Licence

Propriétaire — WhatBot Pro © 2024
