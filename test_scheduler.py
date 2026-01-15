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

# ==================== Test Scheduler ====================

@patch('routes.scheduler_routes.start_scheduler')
def test_start_scheduler(mock_start):
    """Test démarrer le scheduler"""
    mock_start.return_value = {"success": True, "message": "Scheduler started"}
    
    response = client.post("/scheduler/start")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    print("✅ test_start_scheduler PASSED")

@patch('routes.scheduler_routes.stop_scheduler')
def test_stop_scheduler(mock_stop):
    """Test arrêter le scheduler"""
    mock_stop.return_value = {"success": True, "message": "Scheduler stopped"}
    
    response = client.post("/scheduler/stop")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "stopped"
    print("✅ test_stop_scheduler PASSED")

@patch('routes.scheduler_routes.get_scheduler_status')
def test_get_scheduler_status(mock_status):
    """Test obtenir le statut du scheduler"""
    mock_status.return_value = {
        "running": True,
        "scheduled_jobs": 2,
        "jobs": [
            {
                "job_id": "scrape_123",
                "source_id": "123",
                "frequency_hours": 24
            },
            {
                "job_id": "scrape_456",
                "source_id": "456",
                "frequency_hours": 12
            }
        ]
    }
    
    response = client.get("/scheduler/status")
    
    assert response.status_code == 200
    data = response.json()
    assert data["running"] == True
    assert data["scheduled_jobs"] == 2
    print("✅ test_get_scheduler_status PASSED")

@patch('routes.scheduler_routes.schedule_source')
def test_schedule_source(mock_schedule):
    """Test programmer une source"""
    source_id = str(ObjectId())
    mock_schedule.return_value = {
        "success": True,
        "job_id": f"scrape_{source_id}",
        "frequency_hours": 24
    }
    
    response = client.post("/scheduler/schedule", json={
        "source_id": source_id,
        "frequency_hours": 24
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["frequency_hours"] == 24
    print("✅ test_schedule_source PASSED")

@patch('routes.scheduler_routes.unschedule_source')
def test_unschedule_source(mock_unschedule):
    """Test déprogrammer une source"""
    source_id = str(ObjectId())
    mock_unschedule.return_value = {
        "success": True,
        "message": f"Job scrape_{source_id} removed"
    }
    
    response = client.delete(f"/scheduler/unschedule/{source_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    print("✅ test_unschedule_source PASSED")

@patch('routes.scheduler_routes.reschedule_all_sources')
def test_reschedule_all(mock_reschedule):
    """Test re-programmer toutes les sources"""
    mock_reschedule.return_value = {
        "success": True,
        "scheduled_count": 5
    }
    
    response = client.post("/scheduler/reschedule-all")
    
    assert response.status_code == 200
    data = response.json()
    assert data["scheduled_count"] == 5
    print("✅ test_reschedule_all PASSED")

@patch('routes.scheduler_routes.get_job_details')
def test_get_job_details(mock_details):
    """Test obtenir les détails d'un job"""
    source_id = str(ObjectId())
    mock_details.return_value = {
        "job_id": f"scrape_{source_id}",
        "source_id": source_id,
        "frequency_hours": 24,
        "next_run_time": "2026-01-16 10:00:00"
    }
    
    response = client.get(f"/scheduler/job/{source_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["frequency_hours"] == 24
    print("✅ test_get_job_details PASSED")

@patch('routes.scheduler_routes.scrape_source_job')
def test_scrape_source_job(mock_scrape):
    """Test tester le scraping d'une source"""
    source_id = str(ObjectId())
    mock_scrape.return_value = {
        "success": True,
        "source_name": "Example",
        "items_count": 10,
        "document_id": str(ObjectId())
    }
    
    response = client.post(f"/scheduler/test-scrape/{source_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["items_count"] == 10
    print("✅ test_scrape_source_job PASSED")

@patch('routes.scheduler_routes.start_scheduler')
def test_health_check(mock_start):
    """Test vérification de santé"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    print("✅ test_health_check PASSED")
