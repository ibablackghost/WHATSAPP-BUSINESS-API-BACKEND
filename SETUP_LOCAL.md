# WhatBot Pro — Installation locale (sans Docker)

Configuration minimale : **Python + SQLite**, pas de PostgreSQL ni Redis.

## Prérequis

- Python **3.12**
- Git (optionnel)

## 1. Environnement virtuel

```powershell
cd whatbot_pro
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Variables d'environnement

Le fichier `.env` est déjà configuré pour le mode local :

```env
DJANGO_SETTINGS_MODULE=whatbot_pro.settings.local
```

Sinon :

```powershell
copy .env.local.example .env
```

## 3. Base de données

```powershell
$env:DJANGO_SETTINGS_MODULE="whatbot_pro.settings.local"
python manage.py migrate
python manage.py seed_data
```

Un fichier **`db.sqlite3`** est créé à la racine de `whatbot_pro/`.

## 4. Lancer le serveur

```powershell
python manage.py runserver
```

Ou avec le script :

```powershell
.\scripts\dev.ps1
```

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/health/ | Santé API |
| http://127.0.0.1:8000/api/docs/ | Swagger |
| http://127.0.0.1:8000/admin/ | Admin Django |

## Compte démo (après seed)

| Champ | Valeur |
|-------|--------|
| Email | `admin@whatbot.pro` |
| Mot de passe | `Admin@WhatBot2024!` |

## API — connexion

```http
POST http://127.0.0.1:8000/api/v1/auth/login/
Content-Type: application/json

{"email": "admin@whatbot.pro", "password": "Admin@WhatBot2024!"}
```

Puis sur chaque requête :

```http
Authorization: Bearer <access_token>
X-Organization-ID: <uuid-organisation>
```

(L’UUID organisation est retourné après login ou via `GET /api/v1/organizations/`)

## Mode local : ce qui est désactivé / simplifié

| Composant | Comportement |
|-----------|----------------|
| PostgreSQL | Remplacé par **SQLite** |
| Redis | **Non requis** — WebSockets en mémoire |
| Celery | Tâches exécutées **de façon synchrone** (pas de worker à lancer) |
| pgvector | Embeddings FAQ en **JSON** (recherche sémantique en Python) |

## WebSockets

| URL | Usage |
|-----|--------|
| `ws://127.0.0.1:8000/ws?token=<JWT>` | Hub principal (ping/pong, notifications user) |
| `ws://127.0.0.1:8000/ws/conversations/<uuid>/?token=<JWT>` | Chat temps réel |
| `ws://127.0.0.1:8000/ws/agents/?token=<JWT>` | Présence agents |
| `ws://127.0.0.1:8000/ws/notifications/?token=<JWT>` | Campagnes / alertes |

Le JWT est le **access token** retourné par `POST /api/v1/auth/login/`.

Exemple JavaScript :

```javascript
const token = "eyJ..."; // access token
const ws = new WebSocket(`ws://127.0.0.1:8000/ws?token=${token}`);
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.send(JSON.stringify({ type: "ping" }));
```

## Webhook WhatsApp

Meta nécessite une URL **HTTPS publique** (ex. **Railway**). Voir `RAILWAY-DEPLOY.md`.  
Pour PostgreSQL en local : `SETUP-POSTGRES.md`.

## Tests

```powershell
$env:DJANGO_SETTINGS_MODULE="whatbot_pro.settings.test"
pytest
```

## Passer à PostgreSQL / Redis plus tard

Quand tu voudras Docker ou la prod :

1. `DJANGO_SETTINGS_MODULE=whatbot_pro.settings.dev` ou `prod`
2. PostgreSQL + extension `vector` (optionnel)
3. Redis + `celery -A whatbot_pro worker`

Voir `docker-compose.yml` et `README.md`.
