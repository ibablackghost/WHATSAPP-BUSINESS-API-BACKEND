# Déploiement Docker (app + PostgreSQL + Redis)

## Faut-il « builder » la base de données ?

**En général : non.**

| Composant | Approche |
|-----------|----------|
| **PostgreSQL** | Image officielle `pgvector/pgvector:pg15` (déjà dans le projet) |
| **Redis** | Image officielle `redis:7-alpine` |
| **Application Django** | **Build** avec le `Dockerfile` (cible `production`) |

La base n’a pas besoin d’image custom : les données persistent dans un **volume Docker** (`postgres_data`).  
L’extension **pgvector** est activée au premier démarrage via `docker/postgres/init/01-pgvector.sql`.

Tu ne « build » la DB que si tu as des besoins très spécifiques (extensions rares, scripts d’init complexes). Pour WhatBot Pro, l’image pgvector suffit.

---

## Fichiers du projet

| Fichier | Rôle |
|---------|------|
| `docker-compose.postgres.yml` | Dev : **DB + Redis seulement** (Django en local) |
| `docker-compose.yml` | Dev : stack complète (volumes code, target `development`) |
| `docker-compose.prod.yml` | **Prod** : DB + Redis + web + Celery |
| `Dockerfile` | Image Python (`development` / `production`) |

---

## Déploiement production (tout en Docker)

### 1. Préparer l’environnement

```powershell
cd whatbot_pro
copy .env.docker.example .env.docker
# Éditer .env.docker : POSTGRES_PASSWORD, SECRET_KEY, ALLOWED_HOSTS, Meta…
```

### 2. Builder et lancer

```powershell
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

### 3. Vérifier

```powershell
docker compose -f docker-compose.prod.yml ps
curl http://127.0.0.1:8000/health/
```

### 4. Données initiales (optionnel)

```powershell
docker compose -f docker-compose.prod.yml exec web python manage.py seed_data
```

### 5. Webhook WhatsApp

Expose l’URL publique de `web` (HTTPS) vers :

`https://TON-DOMAINE/api/v1/whatsapp/webhook/`

En local : `ngrok http 8000` (ou le port `WEB_PORT`).

---

## Ce qui est build vs tiré

```text
docker compose -f docker-compose.prod.yml build
  → construit l’image whatbot_pro-web (et celery_*)

docker compose up
  → télécharge pgvector:pg15 et redis:7-alpine (pas de build)
  → crée le volume postgres_data (données persistantes)
```

---

## Commandes utiles

```powershell
# Logs
docker compose -f docker-compose.prod.yml logs -f web

# Migrations manuelles
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Shell Django
docker compose -f docker-compose.prod.yml exec web python manage.py shell

# Arrêter (garde les données)
docker compose -f docker-compose.prod.yml down

# Tout supprimer y compris le volume DB (attention)
docker compose -f docker-compose.prod.yml down -v
```

---

## HTTPS / domaine

En production sur un VPS :

1. `docker compose -f docker-compose.prod.yml up -d` (app sur port 8000 interne)
2. **Nginx** ou **Traefik** devant avec certificat Let’s Encrypt
3. `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS` = ton domaine
4. `SECURE_SSL_REDIRECT=false` dans `.env.docker` si TLS est terminé au proxy (recommandé)

---

## Alternative : Railway

Sur Railway, PostgreSQL est souvent un **service managé** (pas un conteneur que tu build).  
Tu déploies seulement l’image **web** ; `DATABASE_URL` est injectée par Railway.

Docker Compose complet = idéal pour **VPS / serveur dédié** ou **dev identique à la prod**.
