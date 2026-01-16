# Tests Suite

Ce dossier contient tous les tests unitaires et d'intégration pour l'application.

## Structure des Tests

- `test_main.py` - Tests généraux de l'application (scraping HTML, URLs invalides)
- `test_config.py` - Tests de configuration (crawler config, stats)
- `test_search.py` - Tests de recherche (keywords, regex)
- `test_sources.py` - Tests de gestion des sources (CRUD)
- `test_scheduler.py` - Tests du scheduler (jobs, scheduling)
- `test_rss.py` - Tests des flux RSS
- `test_social_media.py` - Tests des réseaux sociaux
- `test_integration.py` - Tests d'intégration end-to-end

## Lancer les Tests

### Tous les tests
```bash
pytest tests/
```

### Un fichier spécifique
```bash
pytest tests/test_main.py
```

### Avec couverture
```bash
pytest tests/ --cov=. --cov-report=html
```

### Mode verbose
```bash
pytest tests/ -v
```

## Prérequis

- MongoDB doit être accessible (connexion via MONGO_URI dans .env)
- Toutes les dépendances installées (`pip install -r requirements.txt`)
- Variables d'environnement configurées dans `.env`

## Mocking

Les tests utilisent `unittest.mock` pour simuler:
- Connexions MongoDB
- Requêtes HTTP externes
- Configuration du crawler
- Réponses API

Cela permet de tester sans dépendances externes et d'éviter les effets de bord.
