from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from db import sources_collection
from datetime import datetime, UTC
from bson import ObjectId

router = APIRouter(prefix="/sources", tags=["sources"])

# ==================== Models ====================
class SourceCreate(BaseModel):
    """Modèle pour créer une source"""
    name: str
    url: str
    source_type: str  # website, blog, rss, twitter, facebook, linkedin
    frequency: int = 24  # heures entre les scrapes
    selector: Optional[str] = None  # CSS selector pour HTML/XML
    limit: int = 10  # Nombre maximum d'éléments à scraper
    active: bool = True
    description: Optional[str] = None

class SourceUpdate(BaseModel):
    """Modèle pour mettre à jour une source"""
    name: Optional[str] = None
    url: Optional[str] = None
    frequency: Optional[int] = None
    selector: Optional[str] = None
    limit: Optional[int] = None
    active: Optional[bool] = None
    description: Optional[str] = None

class SourceResponse(SourceCreate):
    """Modèle de réponse"""
    id: str
    created_at: datetime
    last_scraped: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# ==================== Routes ====================

@router.post("/", response_model=SourceResponse, status_code=201)
def create_source(source: SourceCreate):
    """Créer une nouvelle source"""
    try:
        document = {
            **source.model_dump(),
            "created_at": datetime.now(UTC),
            "last_scraped": None,
            "scrape_count": 0
        }
        result = sources_collection.insert_one(document)
        document["id"] = str(result.inserted_id)
        return document
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating source: {str(e)}")

@router.get("/", response_model=List[SourceResponse])
def list_sources(active_only: bool = False):
    """Lister toutes les sources"""
    try:
        query = {"active": True} if active_only else {}
        sources = list(sources_collection.find(query))
        
        # Formater les réponses
        return [
            {
                **source,
                "id": str(source["_id"])
            } for source in sources
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sources: {str(e)}")

@router.get("/{source_id}", response_model=SourceResponse)
def get_source(source_id: str):
    """Récupérer une source spécifique"""
    try:
        source = sources_collection.find_one({"_id": ObjectId(source_id)})
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        source["id"] = str(source["_id"])
        return source
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching source: {str(e)}")

@router.put("/{source_id}", response_model=SourceResponse)
def update_source(source_id: str, source_update: SourceUpdate):
    """Mettre à jour une source"""
    try:
        update_data = {k: v for k, v in source_update.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        result = sources_collection.update_one(
            {"_id": ObjectId(source_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Source not found")
        
        # Récupérer le document mis à jour
        source = sources_collection.find_one({"_id": ObjectId(source_id)})
        source["id"] = str(source["_id"])
        return source
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating source: {str(e)}")

@router.delete("/{source_id}", status_code=204)
def delete_source(source_id: str):
    """Supprimer une source"""
    try:
        result = sources_collection.delete_one({"_id": ObjectId(source_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Source not found")
        
        return {"message": "Source deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting source: {str(e)}")

@router.patch("/{source_id}/toggle", response_model=SourceResponse)
def toggle_source_active(source_id: str):
    """Activer/désactiver une source"""
    try:
        source = sources_collection.find_one({"_id": ObjectId(source_id)})
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        new_active = not source.get("active", True)
        result = sources_collection.update_one(
            {"_id": ObjectId(source_id)},
            {"$set": {"active": new_active}}
        )
        
        source = sources_collection.find_one({"_id": ObjectId(source_id)})
        source["id"] = str(source["_id"])
        return source
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error toggling source: {str(e)}")
