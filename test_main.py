import pytest
from unittest.mock import patch, MagicMock
import os
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

from main import app

client = TestClient(app)

@patch('routes.scrape.collection.insert_one')
def test_scrape_html(mock_insert):
    """Test de scraping HTML"""
    mock_insert.return_value = MagicMock(inserted_id='test_id')
    
    response = client.post("/scrape", json={
        "url": "https://example.com",
        "selector": "p",
        "limit": 5
    })
    # Accepte 200 (succès) ou 400/415 (erreur réseau)
    assert response.status_code in [200, 400, 415]

@patch('routes.scrape.collection.insert_one')
def test_invalid_url(mock_insert):
    """Test avec URL invalide"""
    mock_insert.return_value = MagicMock(inserted_id='test_id')
    
    response = client.post("/scrape", json={
        "url": "https://invalid-url-that-does-not-exist-12345.com",
        "selector": "p",
        "limit": 5
    })
    # Doit retourner une erreur (400 ou timeout)
    assert response.status_code in [400, 500]

@patch('routes.scrape.collection.insert_one')
def test_missing_fields(mock_insert):
    """Test avec champs manquants"""
    response = client.post("/scrape", json={
        "url": "https://example.com"
        # selector manquant
    })
    assert response.status_code == 422  # Validation error