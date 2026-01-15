# Web Analytics Project - Application Crawler Avancée

Une application **FastAPI** complète pour la collecte, le traitement et l'analyse de données web avec support avancé pour le scraping, les flux RSS et les réseaux sociaux.

## 📋 Table des matières
- [Vue d'ensemble](#vue-densemble)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [API Endpoints](#api-endpoints)
- [Docker](#docker)

---

## 🎯 Vue d'ensemble

Cette application est un **système complet de web scraping** avec les capacités suivantes:

| Phase | Description | Statut |
|-------|-------------|--------|
| **Phase 1** | Collecte de données et recherche par mots-clés | ✅ Complet |
| **Phase 2** | Programmation automatique des tâches | ✅ Complet |
| **Phase 3a** | Support des flux RSS | ✅ Complet |
| **Phase 3b** | Intégration réseaux sociaux | ✅ Complet |
| **Phase 4** | Containerisation Docker | ✅ Complet |

---

## ✨ Fonctionnalités

### 🔷 Phase 1: Collecte de Données

**Scraping Web Avancé**
- Scrape multiple formats: HTML, XML, PDF, CSV, TXT
- Extraction intelligente du contenu avec **BeautifulSoup4**
- Support des sélecteurs CSS personnalisés
- Gestion des timeout et des erreurs

**Gestion des Sources**
- Enregistrement et gestion des sources de scraping
- CRUD complet: Créer, Lire, Mettre à jour, Supprimer
- Validation Pydantic V2 des données
- Métadonnées enrichies (catégorie, tags, etc.)

**Recherche par Mots-clés**
- Recherche regex flexible dans les documents scraped
- Filtrage par date
- Support de la casse sensible/insensible
- Pagination des résultats

### 🔷 Phase 2: Planification Automatique

**Scheduler APScheduler**
- Programmation automatique des tâches de scraping
- Déclenchement par intervalle configurable
- Gestion des jobs: démarrage, arrêt, reschédulage
- Persévérance: les jobs survivent aux redémarrages via MongoDB
- Monitoring et statistiques des tâches

**Configuration Globale**
- Fréquence globale de scraping ajustable
- Limite de hits par source
- Timeout configurable
- Gestion des tentatives (retry)

### 🔷 Phase 3a: Support RSS

**Parseur RSS**
- Parsing de flux RSS/Atom avec **feedparser**
- Extraction automatique des entrées
- Scraping du contenu de chaque article
- Stockage avec métadonnées (auteur, date, categorie)

**Endpoints RSS**
- Parse-feed: Analyser un flux RSS
- Scrape-rss: Récupérer et stocker les articles
- Add-source: Enregistrer une source RSS
- Get-sources: Lister les sources RSS
- Get-latest: Récupérer les articles récents
- Refresh: Mettre à jour manuellement un flux

### 🔷 Phase 3b: Intégration Réseaux Sociaux

**Support Multi-plateforme**
- **Twitter/X**: Tweets et recherches
- **Instagram**: Posts et hashtags
- **Facebook**: Contenu public et pages
- **LinkedIn**: Posts professionnels et articles

**Fonctionnalités Sociales**
- Connexion à chaque plateforme
- Scraping de contenu public
- Récupération de statistiques (likes, shares, etc.)
- Tests de connexion à chaque source
- Stockage du contenu avec métadonnées complètes

---

## 🏗️ Architecture

### Structure du Projet

```
webanalproject/
├── main.py                 # Point d'entrée FastAPI
├── db.py                   # Connexion MongoDB
├── models.py               # Modèles Pydantic
├── scheduler.py            # Gestion APScheduler
├── requirements.txt        # Dépendances Python
├── .env.example            # Template de configuration
│
├── routes/                 # Modules de fonctionnalités
│   ├── scrape.py          # Scraping web
│   ├── sources.py         # CRUD sources
│   ├── config.py          # Configuration globale
│   ├── search.py          # Recherche par mots-clés
│   ├── scheduler_routes.py # Endpoints scheduler
│   ├── rss.py             # Gestion des flux RSS
│   └── social_media.py    # Intégration réseaux sociaux
│
├── frontend/              # Interface utilisateur
├── Dockerfile             # Containerisation
├── docker-compose.yml     # Environnement dev
└── docker-compose.prod.yml # Configuration production
```

### Stack Technologique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Framework Web | FastAPI | 0.128.0 |
| Serveur | Uvicorn | 0.40.0 |
| Base de données | MongoDB | 7.0+ |
| Scraping | BeautifulSoup4 | 4.14.3 |
| PDF | pypdf | 6.6.0 |
| RSS | feedparser | - |
| Scheduling | APScheduler | 3.11.2 |
| Validation | Pydantic | 2.12.5 |
| Tests | pytest | 9.0.2 |
| Python | 3.13.9 | - |

---

## 📦 Installation

### Prérequis
- Python 3.13+
- MongoDB 7.0+
- pip

### Étapes d'installation

1. **Cloner le projet**
```bash
git clone <repo-url>
cd webanalproject
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
# Copier le template
cp .env.example .env

# Éditer .env avec vos paramètres
# - MONGO_URI: mongodb://user:pass@host:port/db
# - MONGODB_DB: nom de la base de données
# - API_HOST: localhost
# - API_PORT: 8000
```

5. **Lancer l'application**
```bash
python main.py
# L'API sera accessible sur http://localhost:8000
```

---

## ⚙️ Configuration

### Variables d'environnement (.env)

```env
# MongoDB
MONGO_URI=mongodb://localhost:27017/web_analytics
MONGODB_DB=web_analytics

# API
API_HOST=localhost
API_PORT=8000

# Scraping
SCRAPE_TIMEOUT=10
MAX_RETRIES=3

# Scheduler
SCHEDULER_INTERVAL=3600  # 1 heure par défaut
```

### Configuration du Crawler (via API)

```bash
# Récupérer la configuration actuelle
curl http://localhost:8000/config

# Mettre à jour la configuration
curl -X PUT http://localhost:8000/config \
  -H "Content-Type: application/json" \
  -d '{
    "global_frequency": 3600,
    "max_hits_per_source": 100,
    "timeout": 10,
    "retry_count": 3
  }'
```

---

## 🚀 Utilisation

### Exemple complet d'utilisation

#### 1. Créer une source
```bash
curl -X POST http://localhost:8000/sources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "BBC News",
    "url": "https://www.bbc.com/news",
    "category": "news",
    "tags": ["news", "politics"]
  }'
```

#### 2. Scraper une URL
```bash
curl -X POST http://localhost:8000/scrape/manual \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "selector": "article",
    "content_type": "html"
  }'
```

#### 3. Ajouter un flux RSS
```bash
curl -X POST http://localhost:8000/rss/add-source \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tech News RSS",
    "url": "https://example.com/feed.xml",
    "category": "technology"
  }'
```

#### 4. Scraper un flux RSS
```bash
curl -X POST http://localhost:8000/rss/scrape-rss \
  -H "Content-Type: application/json" \
  -d '{
    "rss_url": "https://example.com/feed.xml"
  }'
```

#### 5. Ajouter une source réseaux sociaux
```bash
curl -X POST http://localhost:8000/social/add-source \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "twitter",
    "handle": "@username",
    "api_key": "your-api-key"
  }'
```

#### 6. Rechercher du contenu
```bash
curl "http://localhost:8000/search?keyword=python&case_sensitive=false&limit=50"
```

#### 7. Planifier un scraping automatique
```bash
curl -X POST http://localhost:8000/scheduler/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "507f1f77bcf86cd799439011",
    "interval_seconds": 3600
  }'
```

---

## 📡 API Endpoints

### Scraping (`/scrape`)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/scrape/manual` | Scraper une URL donnée |
| POST | `/scrape/by-source` | Scraper une source enregistrée |
| GET | `/scrape/health` | Vérifier l'état de l'API |

### Sources (`/sources`)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/sources` | Créer une nouvelle source |
| GET | `/sources` | Lister toutes les sources |
| GET | `/sources/{id}` | Récupérer une source |
| PUT | `/sources/{id}` | Mettre à jour une source |
| DELETE | `/sources/{id}` | Supprimer une source |

### Configuration (`/config`)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/config` | Récupérer la configuration |
| PUT | `/config` | Mettre à jour la configuration |
| GET | `/config/stats` | Statistiques du crawler |
| POST | `/config/toggle-pause` | Pause/Reprendre le crawler |

### Recherche (`/search`)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/search` | Rechercher par mot-clé |

### Scheduler (`/scheduler`)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/scheduler/schedule` | Planifier une tâche |
| POST | `/scheduler/unschedule` | Arrêter une tâche planifiée |
| POST | `/scheduler/reschedule-all` | Re-planifier toutes les sources |
| GET | `/scheduler/jobs` | Lister les jobs actifs |
| POST | `/scheduler/start` | Démarrer le scheduler |
| POST | `/scheduler/stop` | Arrêter le scheduler |
| GET | `/scheduler/status` | État du scheduler |

### RSS (`/rss`)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/rss/parse` | Parser un flux RSS |
| POST | `/rss/scrape-rss` | Scraper un flux RSS |
| POST | `/rss/add-source` | Enregistrer une source RSS |
| GET | `/rss/get-sources` | Lister les sources RSS |
| GET | `/rss/get-latest` | Articles RSS récents |
| POST | `/rss/refresh` | Mettre à jour un flux |

### Réseaux Sociaux (`/social`)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/social/add-source` | Ajouter une source sociales |
| GET | `/social/get-sources` | Lister les sources sociales |
| POST | `/social/test-connection` | Tester une connexion |
| POST | `/social/scrape` | Scraper du contenu social |
| GET | `/social/get-posts` | Récupérer les posts |
| GET | `/social/stats` | Statistiques sociales |

---

## 🐳 Docker

### Lancer avec Docker Compose (Développement)

```bash
# Démarrer les services
docker-compose up -d

# Vérifier l'état
docker-compose ps

# Afficher les logs
docker-compose logs -f api

# Arrêter les services
docker-compose down
```

L'API sera accessible sur `http://localhost:8000`

### Lancer en Production

```bash
# Avec docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d

# Vérifier la santé
curl http://localhost:8000/scrape/health

# Afficher les logs JSON
docker-compose -f docker-compose.prod.yml logs api
```

### Build personnalisé

```bash
# Construire l'image
docker build -t web-analytics:latest .

# Lancer le container
docker run -d \
  --name analytics \
  -p 8000:8000 \
  -e MONGO_URI=mongodb://mongo:27017/web_analytics \
  web-analytics:latest

# Accéder aux logs
docker logs analytics
```

---

## 🧪 Tests

Tous les tests unitaires et d'intégration sont inclus.

```bash
# Lancer tous les tests
pytest -v

# Tests par module
pytest test_sources.py -v      # Sources CRUD
pytest test_config.py -v       # Configuration
pytest test_search.py -v       # Recherche
pytest test_scheduler.py -v    # Scheduler
pytest test_rss.py -v          # RSS
pytest test_social_media.py -v # Réseaux sociaux

# Avec rapport de couverture
pytest --cov=routes --cov=scheduler --cov=db
```

---

## 📊 Base de données

### Collections MongoDB

| Collection | Description |
|-----------|-------------|
| `scraped_data` | Contenu scraped avec métadonnées |
| `sources` | Sources de scraping enregistrées |
| `rss_sources` | Sources de flux RSS |
| `rss_entries` | Articles RSS parsés |
| `social_sources` | Sources réseaux sociaux |
| `social_posts` | Posts sociaux collectés |
| `crawler_config` | Configuration globale du crawler |
| `scheduler_jobs` | Historique des jobs scheduler |

---

## 🔐 Sécurité

- ✅ Variables d'environnement sécurisées (pas de hardcoding)
- ✅ MongoDB avec authentification
- ✅ Validation Pydantic V2 stricte
- ✅ User non-root dans Docker
- ✅ Health checks intégrés
- ✅ Gestion des erreurs complète

---

## 📚 Documentation supplémentaire

- [Swagger API](http://localhost:8000/docs) - Documentation interactive
- [ReDoc](http://localhost:8000/redoc) - Documentation alternative
- [systemdesign.md](systemdesign.md) - Architecture détaillée

---

## 🤝 Support

Pour les problèmes ou questions:
1. Consulter les logs: `docker-compose logs api`
2. Vérifier la configuration: `curl http://localhost:8000/config`
3. Vérifier la santé: `curl http://localhost:8000/scrape/health`

---

## 📝 Licence

MIT

---

**Dernière mise à jour**: Janvier 2026 | **Version**: 4.0 (Phase 4 complète)
