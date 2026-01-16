import pytest
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from dotenv import load_dotenv
from bson import ObjectId

# Charger les variables d'environnement depuis .env
load_dotenv()

from main import app

client = TestClient(app)

# ==================== Test Sources CRUD ====================

@patch('routes.sources.sources_collection.insert_one')
def test_create_source(mock_insert):
    """Test créer une source"""
    mock_insert.return_value = MagicMock(inserted_id=ObjectId())
    
    response = client.post("/sources/", json={
        "name": "Example Website",
        "url": "https://example.com",
        "source_type": "website",
        "frequency": 24,
        "selector": "p",
        "description": "Test source"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Example Website"
    assert data["url"] == "https://example.com"
    print("✅ test_create_source PASSED")

@patch('routes.sources.sources_collection.find')
def test_list_sources(mock_find):
    """Test lister les sources"""
    mock_source = {
        "_id": ObjectId(),
        "name": "Example",
        "url": "https://example.com",
        "source_type": "website",
        "frequency": 24,
        "active": True,
        "created_at": "2026-01-15T00:00:00Z"
    }
    mock_find.return_value = [mock_source]
    
    response = client.get("/sources/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    print("✅ test_list_sources PASSED")

@patch('routes.sources.sources_collection.find_one')
def test_get_source(mock_find_one):
    """Test récupérer une source spécifique"""
    source_id = str(ObjectId())
    mock_source = {
        "_id": ObjectId(source_id),
        "name": "Example",
        "url": "https://example.com",
        "source_type": "website",
        "frequency": 24,
        "active": True,
        "created_at": "2026-01-15T00:00:00Z"
    }
    mock_find_one.return_value = mock_source
    
    response = client.get(f"/sources/{source_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Example"
    print("✅ test_get_source PASSED")

@patch('routes.sources.sources_collection.update_one')
@patch('routes.sources.sources_collection.find_one')
def test_update_source(mock_find_one, mock_update_one):
    """Test mettre à jour une source"""
    source_id = str(ObjectId())
    mock_update_one.return_value = MagicMock(matched_count=1)
    mock_find_one.return_value = {
        "_id": ObjectId(source_id),
        "name": "Updated Name",
        "url": "https://example.com",
        "source_type": "website",
        "frequency": 48,
        "active": True,
        "created_at": "2026-01-15T00:00:00Z"
    }
    
    response = client.put(f"/sources/{source_id}", json={
        "frequency": 48
    })
    
    assert response.status_code == 200
    print("✅ test_update_source PASSED")

@patch('routes.sources.sources_collection.delete_one')
def test_delete_source(mock_delete_one):
    """Test supprimer une source"""
    source_id = str(ObjectId())
    mock_delete_one.return_value = MagicMock(deleted_count=1)
    
    response = client.delete(f"/sources/{source_id}")
    
    assert response.status_code == 204
    print("✅ test_delete_source PASSED")

@patch('routes.sources.sources_collection.find_one')
@patch('routes.sources.sources_collection.update_one')
def test_toggle_source(mock_update_one, mock_find_one):
    """Test activer/désactiver une source"""
    source_id = str(ObjectId())
    mock_update_one.return_value = MagicMock(matched_count=1)
    mock_find_one.return_value = {
        "_id": ObjectId(source_id),
        "name": "Example",
        "url": "https://example.com",
        "source_type": "website",
        "frequency": 24,
        "active": False,
        "created_at": "2026-01-15T00:00:00Z"
    }
    
    response = client.patch(f"/sources/{source_id}/toggle")
    
    assert response.status_code == 200
    print("✅ test_toggle_source PASSED")

# ==================== Test Scrape existant ====================

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
    mock_insert.return_value = MagicMock(inserted_id=ObjectId())
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
    assert response.status_code == 200
    print("✅ test_scrape_html PASSED")
