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

# ==================== Test RSS ====================

@patch('routes.rss.feedparser.parse')
def test_parse_rss_feed(mock_parse):
    """Test parser un flux RSS"""
    mock_feed = MagicMock()
    mock_feed.bozo = False
    mock_feed.feed = {
        "title": "Example Feed",
        "description": "Test RSS feed",
        "link": "https://example.com",
        "language": "en"
    }
    
    mock_entry = MagicMock()
    mock_entry.get = MagicMock(side_effect=lambda key, default="": {
        "title": "Test Article",
        "link": "https://example.com/article1",
        "summary": "This is a test article",
        "published": "2026-01-15",
        "author": "John Doe"
    }.get(key, default))
    
    mock_feed.entries = [mock_entry]
    mock_parse.return_value = mock_feed
    
    response = client.post("/rss/parse", params={
        "rss_url": "https://example.com/feed.xml",
        "limit": 20
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "feed_info" in data
    assert "entries" in data
    print("✅ test_parse_rss_feed PASSED")

@patch('routes.rss.scraped_collection.insert_one')
@patch('routes.rss.feedparser.parse')
def test_scrape_rss_feed(mock_parse, mock_insert):
    """Test scraper un flux RSS"""
    mock_feed = MagicMock()
    mock_feed.bozo = False
    mock_feed.feed = {
        "title": "Example Feed",
        "description": "Test RSS feed",
        "link": "https://example.com",
        "language": "en"
    }
    
    mock_entry = MagicMock()
    mock_entry.get = MagicMock(side_effect=lambda key, default="": {
        "title": "Test Article",
        "link": "https://example.com/article1",
        "summary": "This is a test article",
        "published": "2026-01-15",
        "author": "John Doe"
    }.get(key, default))
    
    mock_feed.entries = [mock_entry]
    mock_parse.return_value = mock_feed
    mock_insert.return_value = MagicMock(inserted_id=ObjectId())
    
    response = client.post("/rss/scrape-rss", params={
        "rss_url": "https://example.com/feed.xml",
        "limit": 20
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["scraped_entries"] == 1
    print("✅ test_scrape_rss_feed PASSED")

@patch('routes.rss.sources_collection.insert_one')
@patch('routes.rss.feedparser.parse')
def test_add_rss_source(mock_parse, mock_insert):
    """Test ajouter une source RSS"""
    mock_feed = MagicMock()
    mock_feed.bozo = False
    mock_feed.feed = {
        "title": "Example Feed",
        "description": "Test RSS feed",
        "link": "https://example.com",
        "language": "en"
    }
    mock_feed.entries = [MagicMock()]
    mock_parse.return_value = mock_feed
    mock_insert.return_value = MagicMock(inserted_id=ObjectId())
    
    response = client.post("/rss/add-source", json={
        "name": "Example RSS",
        "rss_url": "https://example.com/feed.xml",
        "frequency": 24,
        "limit": 20
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "source" in data
    print("✅ test_add_rss_source PASSED")

@patch('routes.rss.sources_collection.find')
def test_get_rss_sources(mock_find):
    """Test obtenir les sources RSS"""
    mock_source = {
        "_id": ObjectId(),
        "name": "Example RSS",
        "url": "https://example.com/feed.xml",
        "source_type": "rss",
        "frequency": 24
    }
    mock_find.return_value = [mock_source]
    
    response = client.get("/rss/sources")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["sources"]) == 1
    print("✅ test_get_rss_sources PASSED")

@patch('routes.rss.scraped_collection.find')
@patch('routes.rss.sources_collection.find_one')
def test_get_rss_source_latest(mock_find_one, mock_find):
    """Test obtenir les dernières entrées"""
    source_id = str(ObjectId())
    mock_find_one.return_value = {
        "_id": ObjectId(source_id),
        "name": "Example RSS",
        "url": "https://example.com/feed.xml",
        "source_type": "rss"
    }
    
    mock_doc = {
        "_id": ObjectId(),
        "title": "Test Article",
        "summary": "Test summary",
        "published": "2026-01-15",
        "author": "John Doe",
        "scraped_at": datetime.now(UTC)
    }
    
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.limit.return_value = [mock_doc]
    mock_find.return_value = mock_cursor
    
    response = client.get(f"/rss/source/{source_id}/latest", params={"limit": 10})
    
    assert response.status_code == 200
    data = response.json()
    assert "source" in data
    assert "entries" in data
    print("✅ test_get_rss_source_latest PASSED")

@patch('routes.rss.sources_collection.update_one')
@patch('routes.rss.scraped_collection.insert_one')
@patch('routes.rss.sources_collection.find_one')
@patch('routes.rss.feedparser.parse')
def test_refresh_rss_source(mock_parse, mock_find_one, mock_insert, mock_update):
    """Test rafraîchir une source RSS"""
    source_id = str(ObjectId())
    mock_feed = MagicMock()
    mock_feed.bozo = False
    mock_feed.feed = {
        "title": "Example Feed",
        "description": "Test RSS feed"
    }
    
    mock_entry = MagicMock()
    mock_entry.get = MagicMock(side_effect=lambda key, default="": {
        "title": "Test Article",
        "link": "https://example.com/article1",
        "summary": "Test summary",
        "published": "2026-01-15",
        "author": "John Doe"
    }.get(key, default))
    
    mock_feed.entries = [mock_entry]
    mock_parse.return_value = mock_feed
    
    mock_find_one.return_value = {
        "_id": ObjectId(source_id),
        "name": "Example RSS",
        "url": "https://example.com/feed.xml",
        "source_type": "rss",
        "limit": 20
    }
    
    mock_insert.return_value = MagicMock(inserted_id=ObjectId())
    mock_update.return_value = MagicMock(modified_count=1)
    
    response = client.post(f"/rss/refresh/{source_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["entries_scraped"] == 1
    print("✅ test_refresh_rss_source PASSED")
