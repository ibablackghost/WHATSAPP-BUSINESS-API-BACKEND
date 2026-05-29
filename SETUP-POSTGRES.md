# WhatBot Pro — PostgreSQL + Redis (dev local)

Ngrok n'est **plus utilisé**. Webhook WhatsApp → déploiement **Railway** (`RAILWAY-DEPLOY.md`).

---

## Prérequis

- **Docker Desktop** installé et démarré
- **Python 3.12** + venv

---

## Démarrage en 2 commandes

```powershell
cd whatbot_pro
.\scripts\postgres.ps1    # 1ère fois : Docker + migrate + seed
.\scripts\dev.ps1         # API sur http://127.0.0.1:8000
```

---

## Services Docker

| Service | Conteneur | Port local |
|---------|-----------|------------|
| PostgreSQL 15 + pgvector | `whatbot_postgres` | **5433** |
| Redis 7 | `whatbot_redis` | **6380** |

Fichier : `docker-compose.postgres.yml`

```powershell
docker compose -f docker-compose.postgres.yml up -d    # demarrer
docker compose -f docker-compose.postgres.yml down      # arreter
docker compose -f docker-compose.postgres.yml logs -f db
```

---

## Configuration `.env`

Settings Django : **`whatbot_pro.settings.postgres_local`**

| Variable | Valeur |
|----------|--------|
| `POSTGRES_DB` | `whatbot_pro` |
| `POSTGRES_USER` | `whatbot` |
| `POSTGRES_PASSWORD` | `whatbot` |
| `POSTGRES_HOST` | `localhost` |
| `POSTGRES_PORT` | `5433` |
| `REDIS_URL` | `redis://localhost:6380/0` |

---

## Commandes utiles

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py seed_data
python manage.py check_whatsapp
python manage.py dbshell
```

Compte demo : `admin@whatbot.pro` / `Admin@WhatBot2024!`

---

## Ancien mode SQLite

Toujours disponible : `DJANGO_SETTINGS_MODULE=whatbot_pro.settings.local` (fichier `db.sqlite3`, sans Docker).

---

## Ngrok

Ngrok a ete retire du projet et desinstalle sur cette machine (winget + Microsoft Store).  
Webhook WhatsApp : deployer sur **Railway** (`RAILWAY-DEPLOY.md`).
