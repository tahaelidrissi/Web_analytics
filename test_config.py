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

# ==================== Test Config ====================

@patch('routes.config.db')
def test_get_config(mock_db):
    """Test récupérer la configuration"""
    mock_config_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_config_collection
    
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
    
    response = client.get("/config/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["global_frequency"] == 24
    assert data["enabled"] == True
    print("✅ test_get_config PASSED")

@patch('routes.config.db')
def test_update_config(mock_db):
    """Test mettre à jour la configuration"""
    mock_config_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_config_collection
    
    old_config = {
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
    
    new_config = {
        **old_config,
        "global_frequency": 48,
        "updated_at": datetime.now(UTC)
    }
    
    mock_config_collection.find_one.side_effect = [old_config, new_config]
    mock_config_collection.update_one.return_value = MagicMock(modified_count=1)
    
    response = client.put("/config/", json={
        "global_frequency": 48,
        "max_hits_per_source": 100,
        "timeout": 15,
        "retry_count": 3,
        "retry_delay": 5,
        "enabled": True
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["global_frequency"] == 48
    print("✅ test_update_config PASSED")

@patch('routes.config.db')
def test_get_crawler_stats(mock_db):
    """Test obtenir les statistiques du crawler"""
    mock_sources_collection = MagicMock()
    mock_scraped_collection = MagicMock()
    
    def mock_getitem(key):
        if key == "sources":
            return mock_sources_collection
        elif key == "scraped_data":
            return mock_scraped_collection
    
    mock_db.__getitem__.side_effect = mock_getitem
    
    mock_sources_collection.count_documents.side_effect = [10, 8]
    mock_scraped_collection.count_documents.return_value = 150
    mock_scraped_collection.find_one.return_value = {
        "scraped_at": datetime.now(UTC)
    }
    
    response = client.get("/config/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_sources"] == 10
    assert data["active_sources"] == 8
    assert data["total_scraped_documents"] == 150
    print("✅ test_get_crawler_stats PASSED")

@patch('routes.config.db')
def test_reset_config(mock_db):
    """Test réinitialiser la configuration"""
    mock_config_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_config_collection
    
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
    
    mock_config_collection.delete_many.return_value = MagicMock(deleted_count=1)
    mock_config_collection.find_one.return_value = mock_config
    
    response = client.post("/config/reset")
    
    assert response.status_code == 200
    print("✅ test_reset_config PASSED")

@patch('routes.config.db')
def test_toggle_crawler_enabled(mock_db):
    """Test activer/désactiver le crawler"""
    mock_config_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_config_collection
    
    old_config = {
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
    
    new_config = {
        **old_config,
        "enabled": False,
        "updated_at": datetime.now(UTC)
    }
    
    mock_config_collection.find_one.side_effect = [old_config, new_config]
    mock_config_collection.update_one.return_value = MagicMock(modified_count=1)
    
    response = client.patch("/config/toggle")
    
    assert response.status_code == 200
    data = response.json()
    assert data["enabled"] == False
    print("✅ test_toggle_crawler_enabled PASSED")
