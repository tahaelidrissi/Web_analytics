from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import List
from scheduler import (
    schedule_source, unschedule_source, reschedule_all_sources,
    start_scheduler, stop_scheduler, get_scheduler_status, get_job_details,
    scrape_source_job
)

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

# ==================== Models ====================

class ScheduleRequest(BaseModel):
    """Modèle pour programmer une source"""
    source_id: str
    frequency_hours: int = 24
    
    model_config = ConfigDict(from_attributes=True)

class JobStatus(BaseModel):
    """Statut d'un job"""
    job_id: str
    source_id: str
    frequency_hours: int
    next_run_time: str

class SchedulerStatus(BaseModel):
    """Statut du scheduler"""
    running: bool
    scheduled_jobs: int
    jobs: List[dict]

# ==================== Routes ====================

@router.post("/start")
def start_scheduler_endpoint():
    """Démarrer le scheduler"""
    try:
        result = start_scheduler()
        if result["success"]:
            return {"message": "Scheduler started", "status": "running"}
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/stop")
def stop_scheduler_endpoint():
    """Arrêter le scheduler"""
    try:
        result = stop_scheduler()
        if result["success"]:
            return {"message": "Scheduler stopped", "status": "stopped"}
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/status", response_model=SchedulerStatus)
def get_status():
    """Obtenir le statut du scheduler"""
    try:
        status = get_scheduler_status()
        return SchedulerStatus(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/schedule")
def schedule_source_endpoint(request: ScheduleRequest):
    """Programmer une source pour scraping automatique"""
    try:
        result = schedule_source(request.source_id, request.frequency_hours)
        if result["success"]:
            return {
                "message": f"Source {request.source_id} scheduled",
                "job_id": result["job_id"],
                "frequency_hours": result["frequency_hours"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.delete("/unschedule/{source_id}")
def unschedule_source_endpoint(source_id: str):
    """Arrêter le scraping automatique d'une source"""
    try:
        result = unschedule_source(source_id)
        if result["success"]:
            return {"message": result["message"]}
        else:
            raise HTTPException(status_code=404, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/reschedule-all")
def reschedule_all():
    """Re-programmer toutes les sources actives"""
    try:
        result = reschedule_all_sources()
        if result["success"]:
            return {
                "message": "All sources rescheduled",
                "scheduled_count": result["scheduled_count"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/job/{source_id}", response_model=JobStatus)
def get_job_status(source_id: str):
    """Obtenir le statut d'un job spécifique"""
    try:
        job = get_job_details(source_id)
        if job:
            return JobStatus(**job)
        else:
            raise HTTPException(status_code=404, detail=f"Job for source {source_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/test-scrape/{source_id}")
def test_scrape_endpoint(source_id: str):
    """Tester le scraping d'une source immédiatement"""
    try:
        result = scrape_source_job(source_id)
        if result["success"]:
            return {
                "message": "Source scraped successfully",
                "source_name": result.get("source_name"),
                "items_count": result.get("items_count"),
                "document_id": result.get("document_id")
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
