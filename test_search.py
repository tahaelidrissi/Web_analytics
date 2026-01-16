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

# ==================== Test Search ====================

@patch('routes.search.scraped_collection.count_documents')
@patch('routes.search.scraped_collection.find')
def test_search_keywords(mock_find, mock_count):
    """Test recherche par keywords"""
    mock_count.return_value = 2
    
    mock_doc1 = {
        "_id": ObjectId(),
        "url": "https://example.com",
        "source_id": ObjectId(),
        "data": [
            {"index": 1, "value": "Python is a great language"},
            {"index": 2, "value": "Python programming tutorial"}
        ],
        "scraped_at": datetime.now(UTC)
    }
    
    mock_doc2 = {
        "_id": ObjectId(),
        "url": "https://example2.com",
        "source_id": ObjectId(),
        "data": [
            {"index": 1, "value": "Java vs Python comparison"}
        ],
        "scraped_at": datetime.now(UTC)
    }
    
    mock_cursor = MagicMock()
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.sort.return_value = [mock_doc1, mock_doc2]
    mock_find.return_value = mock_cursor
    
    response = client.post("/search/", json={
        "keywords": ["Python"],
        "case_sensitive": False,
        "exact_match": False,
        "limit": 50,
        "skip": 0
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["results"]) == 2
    assert "Python" in data["results"][0]["matched_keywords"]
    print("✅ test_search_keywords PASSED")

@patch('routes.search.scraped_collection.count_documents')
@patch('routes.search.scraped_collection.find')
def test_search_exact_match(mock_find, mock_count):
    """Test recherche exacte"""
    mock_count.return_value = 1
    
    mock_doc = {
        "_id": ObjectId(),
        "url": "https://example.com",
        "source_id": ObjectId(),
        "data": [
            {"index": 1, "value": "FastAPI framework"}
        ],
        "scraped_at": datetime.now(UTC)
    }
    
    mock_cursor = MagicMock()
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.sort.return_value = [mock_doc]
    mock_find.return_value = mock_cursor
    
    response = client.post("/search/", json={
        "keywords": ["FastAPI"],
        "case_sensitive": False,
        "exact_match": True,
        "limit": 50,
        "skip": 0
    })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    print("✅ test_search_exact_match PASSED")

@patch('routes.search.scraped_collection.count_documents')
@patch('routes.search.scraped_collection.find')
def test_search_multiple_keywords(mock_find, mock_count):
    """Test recherche avec plusieurs keywords"""
    mock_count.return_value = 1
    
    mock_doc = {
        "_id": ObjectId(),
        "url": "https://example.com",
        "source_id": ObjectId(),
        "data": [
            {"index": 1, "value": "Python and FastAPI for web development"}
        ],
        "scraped_at": datetime.now(UTC)
    }
    
    mock_cursor = MagicMock()
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.sort.return_value = [mock_doc]
    mock_find.return_value = mock_cursor
    
    response = client.post("/search/", json={
        "keywords": ["Python", "FastAPI"],
        "case_sensitive": False,
        "exact_match": False,
        "limit": 50,
        "skip": 0
    })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert len(data["results"][0]["matched_keywords"]) >= 1
    print("✅ test_search_multiple_keywords PASSED")

@patch('routes.search.scraped_collection.find')
def test_get_top_keywords(mock_find):
    """Test obtenir les keywords les plus fréquents"""
    mock_doc1 = {
        "_id": ObjectId(),
        "data": [
            {"value": "python programming tutorial"},
            {"value": "python is awesome"}
        ]
    }
    
    mock_doc2 = {
        "_id": ObjectId(),
        "data": [
            {"value": "fastapi web framework"}
        ]
    }
    
    mock_find.return_value = [mock_doc1, mock_doc2]
    
    response = client.get("/search/keywords")
    
    assert response.status_code == 200
    data = response.json()
    assert "top_keywords" in data
    assert len(data["top_keywords"]) > 0
    print("✅ test_get_top_keywords PASSED")

@patch('routes.search.scraped_collection.count_documents')
@patch('routes.search.scraped_collection.find')
def test_search_no_results(mock_find, mock_count):
    """Test recherche sans résultats"""
    mock_count.return_value = 0
    mock_cursor = MagicMock()
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.sort.return_value = []
    mock_find.return_value = mock_cursor
    
    response = client.post("/search/", json={
        "keywords": ["NonExistentKeyword"],
        "case_sensitive": False,
        "exact_match": False,
        "limit": 50,
        "skip": 0
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["results"]) == 0
    print("✅ test_search_no_results PASSED")
