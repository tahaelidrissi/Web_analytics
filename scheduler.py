from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from db import sources_collection, collection as scraped_collection, db
import requests
from bs4 import BeautifulSoup
import io
from pypdf import PdfReader
from datetime import datetime, UTC
from bson import ObjectId
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instance globale du scheduler
scheduler = BackgroundScheduler()
scheduled_jobs = {}  # Dictionnaire pour tracker les jobs

def get_config():
    """Récupérer la configuration du crawler"""
    config_collection = db["crawler_config"]
    config = config_collection.find_one({})
    if not config:
        config = {
            "global_frequency": 24,
            "max_hits_per_source": 100,
            "timeout": 15,
            "retry_count": 3,
            "retry_delay": 5,
            "enabled": True
        }
    return config

def scrape_url(url: str, selector=None, limit: int = 10, timeout: int = 15) -> dict:
    """Scraper une URL et retourner les données extraites"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Invalid URL: {response.status_code}",
                "data": []
            }

        content_type = response.headers.get("Content-Type", "").lower()
        data = []

        # HTML / XML
        if "html" in content_type or "xml" in content_type:
            soup = BeautifulSoup(response.text, "html.parser")
            if selector:
                elements = soup.select(selector)[:limit]
            else:
                elements = soup.find_all(["p", "div", "span"])[:limit]
            data = [{"index": i+1, "value": el.get_text(strip=True)} for i, el in enumerate(elements)]

        # TXT / CSV
        elif "text" in content_type:
            lines = response.text.splitlines()[:limit]
            data = [{"index": i+1, "value": line} for i, line in enumerate(lines)]

        # PDF
        elif "pdf" in content_type:
            pdf_file = io.BytesIO(response.content)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            lines = text.splitlines()[:limit]
            data = [{"index": i+1, "value": line} for i, line in enumerate(lines)]

        else:
            return {
                "success": False,
                "error": f"Unsupported content type: {content_type}",
                "data": []
            }

        return {
            "success": True,
            "data": data,
            "content_type": content_type,
            "count": len(data)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": []
        }

def scrape_source_job(source_id: str):
    """Job pour scraper une source spécifique"""
    try:
        source = sources_collection.find_one({"_id": ObjectId(source_id)})
        if not source or not source.get("active"):
            return {"success": False, "error": "Source not found or inactive"}

        config = get_config()
        limit = min(source.get("limit", 10), config["max_hits_per_source"])

        # Scraper
        result = scrape_url(
            url=source["url"],
            selector=source.get("selector"),
            limit=limit,
            timeout=config["timeout"]
        )

        if not result["success"]:
            logger.error(f"Failed to scrape {source['name']}: {result['error']}")
            return result

        # Sauvegarder
        document = {
            "url": source["url"],
            "selector": source.get("selector"),
            "source_id": ObjectId(source_id),
            "source_name": source.get("name"),
            "source_type": source.get("source_type"),
            "limit": limit,
            "count": result["count"],
            "data": result["data"],
            "content_type": result["content_type"],
            "scraped_at": datetime.now(UTC)
        }
        inserted_doc = scraped_collection.insert_one(document)

        # Mettre à jour la source
        sources_collection.update_one(
            {"_id": ObjectId(source_id)},
            {
                "$set": {"last_scraped": datetime.now(UTC)},
                "$inc": {"scrape_count": 1}
            }
        )

        logger.info(f"✅ Successfully scraped {source['name']}: {result['count']} items")
        return {
            "success": True,
            "source_name": source["name"],
            "items_count": result["count"],
            "document_id": str(inserted_doc.inserted_id)
        }

    except Exception as e:
        logger.error(f"Error in scrape_source_job for {source_id}: {str(e)}")
        return {"success": False, "error": str(e)}

def schedule_source(source_id: str, frequency_hours: int):
    """Programmer une source pour scraping automatique"""
    try:
        job_id = f"scrape_{source_id}"
        
        # Supprimer le job existant s'il y en a un
        if job_id in scheduled_jobs:
            scheduler.remove_job(job_id)
            del scheduled_jobs[job_id]
        
        # Ajouter le nouveau job
        job = scheduler.add_job(
            scrape_source_job,
            IntervalTrigger(hours=frequency_hours),
            args=[source_id],
            id=job_id,
            name=f"Scrape source {source_id}",
            replace_existing=True,
            max_instances=1
        )
        
        scheduled_jobs[job_id] = {
            "source_id": source_id,
            "frequency_hours": frequency_hours,
            "job": job
        }
        
        logger.info(f"✅ Scheduled {job_id} every {frequency_hours} hours")
        return {"success": True, "job_id": job_id, "frequency_hours": frequency_hours}
    except Exception as e:
        logger.error(f"Error scheduling source {source_id}: {str(e)}")
        return {"success": False, "error": str(e)}

def unschedule_source(source_id: str):
    """Arrêter le scraping automatique d'une source"""
    try:
        job_id = f"scrape_{source_id}"
        if job_id in scheduled_jobs:
            scheduler.remove_job(job_id)
            del scheduled_jobs[job_id]
            logger.info(f"✅ Unscheduled {job_id}")
            return {"success": True, "message": f"Job {job_id} removed"}
        return {"success": False, "error": f"Job {job_id} not found"}
    except Exception as e:
        logger.error(f"Error unscheduling source {source_id}: {str(e)}")
        return {"success": False, "error": str(e)}

def reschedule_all_sources():
    """Re-programmer toutes les sources actives"""
    try:
        # Supprimer tous les jobs existants
        for job_id in list(scheduled_jobs.keys()):
            scheduler.remove_job(job_id)
        scheduled_jobs.clear()

        # Programmer toutes les sources actives
        sources = sources_collection.find({"active": True})
        count = 0
        for source in sources:
            frequency = source.get("frequency", 24)
            schedule_source(str(source["_id"]), frequency)
            count += 1

        logger.info(f"✅ Rescheduled {count} active sources")
        return {"success": True, "scheduled_count": count}
    except Exception as e:
        logger.error(f"Error rescheduling all sources: {str(e)}")
        return {"success": False, "error": str(e)}

def start_scheduler():
    """Démarrer le scheduler"""
    try:
        if not scheduler.running:
            scheduler.start()
            logger.info("✅ Scheduler started")
            # Re-programmer les sources
            reschedule_all_sources()
        return {"success": True, "message": "Scheduler started"}
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        return {"success": False, "error": str(e)}

def stop_scheduler():
    """Arrêter le scheduler"""
    try:
        if scheduler.running:
            scheduler.shutdown()
            logger.info("✅ Scheduler stopped")
        return {"success": True, "message": "Scheduler stopped"}
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")
        return {"success": False, "error": str(e)}

def get_scheduler_status():
    """Obtenir le statut du scheduler"""
    return {
        "running": scheduler.running,
        "scheduled_jobs": len(scheduled_jobs),
        "jobs": [
            {
                "job_id": job_id,
                "source_id": info["source_id"],
                "frequency_hours": info["frequency_hours"]
            }
            for job_id, info in scheduled_jobs.items()
        ]
    }

def get_job_details(source_id: str):
    """Obtenir les détails d'un job"""
    job_id = f"scrape_{source_id}"
    if job_id in scheduled_jobs:
        info = scheduled_jobs[job_id]
        return {
            "job_id": job_id,
            "source_id": info["source_id"],
            "frequency_hours": info["frequency_hours"],
            "next_run_time": str(info["job"].next_run_time)
        }
    return None
