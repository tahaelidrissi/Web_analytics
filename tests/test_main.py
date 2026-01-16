import pytest
from unittest.mock import patch, MagicMock
import os
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

from main import app

client = TestClient(app)

@patch('routes.scrape.get_config')
@patch('routes.scrape.requests.get')
@patch('routes.scrape.collection.insert_one')
def test_scrape_html(mock_insert, mock_get, mock_config):
    """Test de scraping HTML"""
    mock_config.return_value = {
        "global_frequency": 24,
        "max_hits_per_source": 100,
        "timeout": 15,
        "retry_count": 3
    }
    mock_insert.return_value = MagicMock(inserted_id='test_id')
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "text/html; charset=utf-8"}
    mock_response.text = "<html><body><p>Test content</p><p>Another paragraph</p></body></html>"
    mock_get.return_value = mock_response
    
    response = client.post("/scrape", json={
        "url": "https://example.com",
        "selector": "p",
        "limit": 5
    })
    # Accepte 200 (succès)
    assert response.status_code == 200

@patch('routes.scrape.requests.get')
@patch('routes.scrape.collection.insert_one')
def test_invalid_url(mock_insert, mock_get):
    """Test avec URL invalide"""
    mock_insert.return_value = MagicMock(inserted_id='test_id')
    mock_get.side_effect = Exception("Connection error")
    
    response = client.post("/scrape", json={
        "url": "https://invalid-url-that-does-not-exist-12345.com",
        "selector": "p",
        "limit": 5
    })
    # Doit retourner une erreur (400 ou timeout)
    assert response.status_code in [400, 500]

@patch('routes.scrape.collection.insert_one')
def test_missing_fields(mock_insert):
    """Test avec URL manquante"""
    response = client.post("/scrape", json={
        "selector": "p",
        "limit": 5
        # url manquant - champ requis
    })
    assert response.status_code == 422  # Validation error