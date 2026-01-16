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

# ==================== Test Social Media ====================

@patch('routes.social_media.sources_collection.insert_one')
def test_add_social_media_source(mock_insert):
    """Test ajouter une source de réseau social"""
    mock_insert.return_value = MagicMock(inserted_id=ObjectId())
    
    response = client.post("/social/add-source", json={
        "name": "Example Twitter",
        "platform": "twitter",
        "handle_or_id": "@example",
        "frequency": 6,
        "limit": 20
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "source" in data
    assert data["source"]["platform"] == "twitter"
    print("✅ test_add_social_media_source PASSED")

@patch('routes.social_media.sources_collection.insert_one')
def test_add_invalid_platform(mock_insert):
    """Test ajouter une source avec plateforme invalide"""
    response = client.post("/social/add-source", json={
        "name": "Invalid Platform",
        "platform": "tiktok",
        "handle_or_id": "@example",
        "frequency": 6,
        "limit": 20
    })
    
    assert response.status_code == 400
    print("✅ test_add_invalid_platform PASSED")

@patch('routes.social_media.sources_collection.find')
def test_get_social_media_sources(mock_find):
    """Test obtenir les sources de réseaux sociaux"""
    mock_source = {
        "_id": ObjectId(),
        "name": "Example Twitter",
        "platform": "twitter",
        "handle_or_id": "@example",
        "source_type": "social_media",
        "last_scraped": None,
        "scrape_count": 0
    }
    mock_find.return_value = [mock_source]
    
    response = client.get("/social/sources")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["sources"][0]["platform"] == "twitter"
    print("✅ test_get_social_media_sources PASSED")

@patch('routes.social_media.sources_collection.find')
def test_get_social_media_sources_by_platform(mock_find):
    """Test obtenir les sources filtrées par plateforme"""
    mock_find.return_value = []
    
    response = client.get("/social/sources", params={"platform": "instagram"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["platform_filter"] == "instagram"
    print("✅ test_get_social_media_sources_by_platform PASSED")

@patch('routes.social_media.fetch_twitter_data')
@patch('routes.social_media.sources_collection.find_one')
def test_test_connection_twitter(mock_find_one, mock_fetch):
    """Test la connexion à Twitter"""
    source_id = str(ObjectId())
    mock_find_one.return_value = {
        "_id": ObjectId(source_id),
        "platform": "twitter",
        "handle_or_id": "@example",
        "source_type": "social_media"
    }
    mock_fetch.return_value = {
        "success": True,
        "platform": "twitter",
        "message": "Connection successful"
    }
    
    response = client.post(f"/social/test-connection/{source_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "connected"
    print("✅ test_test_connection_twitter PASSED")

@patch('routes.social_media.sources_collection.update_one')
@patch('routes.social_media.scraped_collection.insert_one')
@patch('routes.social_media.fetch_twitter_data')
@patch('routes.social_media.sources_collection.find_one')
def test_scrape_social_media_source(mock_find_one, mock_fetch, mock_insert, mock_update):
    """Test scraper une source de réseau social"""
    source_id = str(ObjectId())
    mock_find_one.return_value = {
        "_id": ObjectId(source_id),
        "platform": "twitter",
        "handle_or_id": "@example",
        "name": "Example Twitter",
        "url": "twitter://@example",
        "source_type": "social_media",
        "active": True,
        "limit": 20
    }
    
    mock_fetch.return_value = {
        "success": True,
        "platform": "twitter",
        "posts": [
            {
                "id": "tweet123",
                "author": "@example",
                "content": "Test tweet",
                "likes": 10,
                "shares": 2,
                "comments": 5
            }
        ]
    }
    
    mock_insert.return_value = MagicMock(inserted_id=ObjectId())
    mock_update.return_value = MagicMock(modified_count=1)
    
    response = client.post(f"/social/scrape/{source_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["posts_scraped"] == 1
    assert data["platform"] == "twitter"
    print("✅ test_scrape_social_media_source PASSED")

@patch('routes.social_media.scraped_collection.find')
@patch('routes.social_media.sources_collection.find_one')
def test_get_social_media_posts(mock_find_one, mock_find):
    """Test obtenir les posts scrappés"""
    source_id = str(ObjectId())
    mock_find_one.return_value = {
        "_id": ObjectId(source_id),
        "name": "Example Twitter",
        "platform": "twitter",
        "source_type": "social_media"
    }
    
    mock_post = {
        "_id": ObjectId(),
        "author": "@example",
        "content": "Test tweet",
        "likes": 10,
        "shares": 2,
        "comments": 5,
        "posted_at": "2026-01-15",
        "scraped_at": datetime.now(UTC)
    }
    
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.limit.return_value = [mock_post]
    mock_find.return_value = mock_cursor
    
    response = client.get(f"/social/source/{source_id}/posts")
    
    assert response.status_code == 200
    data = response.json()
    assert "source" in data
    assert "posts" in data
    print("✅ test_get_social_media_posts PASSED")

@patch('routes.social_media.scraped_collection.count_documents')
@patch('routes.social_media.sources_collection.count_documents')
def test_get_social_media_stats(mock_sources_count, mock_posts_count):
    """Test obtenir les statistiques"""
    mock_sources_count.side_effect = [1, 1, 0, 0, 2]  # twitter, instagram, facebook, linkedin, total
    mock_posts_count.side_effect = [15, 8, 0, 0, 23]
    
    response = client.get("/social/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert "total_sources" in data
    assert "total_posts_scraped" in data
    assert "by_platform" in data
    print("✅ test_get_social_media_stats PASSED")
