from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Optional
from db import db
from datetime import datetime, UTC
from bson import ObjectId

router = APIRouter(prefix="/config", tags=["config"])

# ==================== Models ====================

class CrawlerConfig(BaseModel):
    """Configuration globale du crawler"""
    global_frequency: int = 24  # heures entre les scrapes
    max_hits_per_source: int = 100  # nombre max d'éléments à scraper par source
    timeout: int = 15  # timeout en secondes
    retry_count: int = 3  # nombre de tentatives en cas d'erreur
    retry_delay: int = 5  # délai entre les tentatives (secondes)
    enabled: bool = True
    
    model_config = ConfigDict(from_attributes=True)

class CrawlerConfigResponse(CrawlerConfig):
    """Réponse de configuration"""
    id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CrawlerStats(BaseModel):
    """Statistiques du crawler"""
    total_sources: int
    active_sources: int
    total_scraped_documents: int
    last_scrape_time: Optional[datetime] = None

# ==================== Routes ====================

def get_or_create_config():
    """Obtenir ou créer la configuration par défaut"""
    config_collection = db["crawler_config"]
    config = config_collection.find_one({})
    
    if not config:
        default_config = {
            "global_frequency": 24,
            "max_hits_per_source": 100,
            "timeout": 15,
            "retry_count": 3,
            "retry_delay": 5,
            "enabled": True,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC)
        }
        result = config_collection.insert_one(default_config)
        config = config_collection.find_one({"_id": result.inserted_id})
    
    return config

@router.get("/", response_model=CrawlerConfigResponse)
def get_config():
    """Récupérer la configuration du crawler"""
    try:
        config = get_or_create_config()
        config["id"] = str(config["_id"])
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting config: {str(e)}")

@router.put("/", response_model=CrawlerConfigResponse)
def update_config(crawler_config: CrawlerConfig):
    """Mettre à jour la configuration du crawler"""
    try:
        config_collection = db["crawler_config"]
        
        update_data = {
            **crawler_config.model_dump(),
            "updated_at": datetime.now(UTC)
        }
        
        config = config_collection.find_one({})
        
        if not config:
            # Créer une nouvelle config
            update_data["created_at"] = datetime.now(UTC)
            result = config_collection.insert_one(update_data)
            config = config_collection.find_one({"_id": result.inserted_id})
        else:
            # Mettre à jour la config existante
            config_collection.update_one(
                {"_id": config["_id"]},
                {"$set": update_data}
            )
            config = config_collection.find_one({"_id": config["_id"]})
        
        config["id"] = str(config["_id"])
        return config
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating config: {str(e)}")

@router.post("/reset", response_model=CrawlerConfigResponse)
def reset_config():
    """Réinitialiser la configuration par défaut"""
    try:
        config_collection = db["crawler_config"]
        config_collection.delete_many({})
        
        config = get_or_create_config()
        config["id"] = str(config["_id"])
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting config: {str(e)}")

@router.get("/stats", response_model=CrawlerStats)
def get_crawler_stats():
    """Obtenir les statistiques du crawler"""
    try:
        sources_collection = db["sources"]
        scraped_collection = db["scraped_data"]
        
        total_sources = sources_collection.count_documents({})
        active_sources = sources_collection.count_documents({"active": True})
        total_documents = scraped_collection.count_documents({})
        
        # Récupérer la dernière date de scrape
        last_doc = scraped_collection.find_one(
            sort=[("scraped_at", -1)]
        )
        last_scrape_time = last_doc.get("scraped_at") if last_doc else None
        
        return CrawlerStats(
            total_sources=total_sources,
            active_sources=active_sources,
            total_scraped_documents=total_documents,
            last_scrape_time=last_scrape_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@router.patch("/toggle", response_model=CrawlerConfigResponse)
def toggle_crawler_enabled():
    """Activer/désactiver le crawler"""
    try:
        config_collection = db["crawler_config"]
        config = get_or_create_config()
        
        new_enabled = not config.get("enabled", True)
        config_collection.update_one(
            {"_id": config["_id"]},
            {"$set": {
                "enabled": new_enabled,
                "updated_at": datetime.now(UTC)
            }}
        )
        
        config = config_collection.find_one({"_id": config["_id"]})
        config["id"] = str(config["_id"])
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling crawler: {str(e)}")
