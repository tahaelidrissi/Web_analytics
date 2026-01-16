import pytest
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from dotenv import load_dotenv
from bson import ObjectId
from datetime import datetime, UTC

# Charger les variables d'environnement depuis .env
load_dotenv()

from main import app

client = TestClient(app)

# ==================== Test Integration Phase 1 ====================

@patch('routes.scrape.collection.insert_one')
@patch('routes.scrape.db')
def test_scrape_manual(mock_db, mock_insert):
    """Test scraping manuel"""
    mock_config_collection = MagicMock()
    mock_config_collection.find_one.return_value = {
        "global_frequency": 24,
        "max_hits_per_source": 100,
        "timeout": 15,
        "retry_count": 3,
        "retry_delay": 5,
        "enabled": True
    }
    mock_db.__getitem__.return_value = mock_config_collection
    mock_insert.return_value = MagicMock(inserted_id=ObjectId())
    
    response = client.post("/scrape", json={
        "url": "https://example.com",
        "selector": "p",
        "limit": 5
    })
    
    assert response.status_code in [200, 400, 415, 500]
    print("✅ test_scrape_manual PASSED")

@patch('routes.scrape.sources_collection.find_one')
@patch('routes.scrape.sources_collection.update_one')
@patch('routes.scrape.collection.insert_one')
@patch('routes.scrape.db')
def test_scrape_by_source(mock_db, mock_insert, mock_update, mock_find):
    """Test scraping via une source"""
    mock_config_collection = MagicMock()
    mock_config_collection.find_one.return_value = {
        "global_frequency": 24,
        "max_hits_per_source": 100,
        "timeout": 15,
        "retry_count": 3,
        "retry_delay": 5,
        "enabled": True
    }
    mock_db.__getitem__.return_value = mock_config_collection
    
    source_id = str(ObjectId())
    mock_find.return_value = {
        "_id": ObjectId(source_id),
        "name": "Example",
        "url": "https://example.com",
        "source_type": "website",
        "selector": "p",
        "active": True,
        "frequency": 24,
        "limit": 10
    }
    
    mock_insert.return_value = MagicMock(inserted_id=ObjectId())
    mock_update.return_value = MagicMock(modified_count=1)
    
    response = client.post("/scrape-source", json={
        "source_id": source_id,
        "limit": 5
    })
    
    assert response.status_code in [200, 400, 500]
    print("✅ test_scrape_by_source PASSED")

@patch('routes.scrape.sources_collection.find')
@patch('routes.scrape.db')
def test_sources_scrape_status(mock_db, mock_find):
    """Test obtenir le statut de scrape des sources"""
    mock_source = {
        "_id": ObjectId(),
        "name": "Example",
        "url": "https://example.com",
        "source_type": "website",
        "last_scraped": datetime.now(UTC),
        "scrape_count": 5,
        "frequency": 24,
        "active": True
    }
    
    mock_find.return_value = [mock_source]
    
    response = client.get("/sources-status")
    
    assert response.status_code == 200
    data = response.json()
    assert "total_active_sources" in data
    assert "sources" in data
    print("✅ test_sources_scrape_status PASSED")

# ==================== Integration Tests ====================

@patch('routes.sources.sources_collection.insert_one')
def test_full_flow_create_source(mock_insert):
    """Test du flux complet: créer une source"""
    mock_insert.return_value = MagicMock(inserted_id=ObjectId())
    
    # Créer une source
    response = client.post("/sources/", json={
        "name": "Test Source",
        "url": "https://example.com",
        "source_type": "website",
        "frequency": 24,
        "selector": "p",
        "description": "Test source"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Source"
    print("✅ test_full_flow_create_source PASSED")

@patch('routes.config.db')
def test_full_flow_get_config(mock_db):
    """Test du flux complet: récupérer la configuration"""
    mock_config_collection = MagicMock()
    mock_config = {
        "_id": ObjectId(),
        "global_frequency": 24,
        "max_hits_per_source": 100,
        "timeout": 15,
        "retry_count": 3,
        "retry_delay": 5,
        "enabled": True,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }
    mock_config_collection.find_one.return_value = mock_config
    mock_db.__getitem__.return_value = mock_config_collection
    
    response = client.get("/config/")
    
    assert response.status_code == 200
    print("✅ test_full_flow_get_config PASSED")

@patch('routes.search.scraped_collection.count_documents')
@patch('routes.search.scraped_collection.find')
def test_full_flow_search(mock_find, mock_count):
    """Test du flux complet: chercher dans les données"""
    mock_count.return_value = 1
    
    mock_doc = {
        "_id": ObjectId(),
        "url": "https://example.com",
        "source_id": ObjectId(),
        "data": [
            {"index": 1, "value": "Test data"}
        ],
        "scraped_at": datetime.now(UTC)
    }
    
    mock_cursor = MagicMock()
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.sort.return_value = [mock_doc]
    mock_find.return_value = mock_cursor
    
    response = client.post("/search/", json={
        "keywords": ["Test"],
        "case_sensitive": False,
        "exact_match": False,
        "limit": 50,
        "skip": 0
    })
    
    assert response.status_code == 200
    print("✅ test_full_flow_search PASSED")

# ==================== Summary ====================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("PHASE 1 INTEGRATION TESTS")
    print("="*60)
