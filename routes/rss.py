from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import feedparser
import requests
from db import collection as scraped_collection, sources_collection, db
from datetime import datetime, UTC
from bson import ObjectId

router = APIRouter(prefix="/rss", tags=["rss"])

# ==================== Models ====================

class RSSFeedInfo(BaseModel):
    """Informations sur un flux RSS"""
    title: str
    url: str
    description: Optional[str] = None
    link: Optional[str] = None
    language: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class RSSEntry(BaseModel):
    """Une entrée RSS"""
    title: str
    link: str
    summary: Optional[str] = None
    published: Optional[str] = None
    author: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class RSSParsedFeed(BaseModel):
    """Flux RSS parsé"""
    feed_info: RSSFeedInfo
    entries: List[RSSEntry]
    total_entries: int

class RSSSourceCreate(BaseModel):
    """Créer une source RSS"""
    name: str
    rss_url: str
    frequency: int = 24
    limit: int = 20
    description: Optional[str] = None
    active: bool = True
    
    model_config = ConfigDict(from_attributes=True)

# ==================== Helper Functions ====================

def parse_rss_feed(rss_url: str, limit: int = 20) -> dict:
    """Parser un flux RSS"""
    try:
        feed = feedparser.parse(rss_url)
        
        if feed.bozo:
            return {
                "success": False,
                "error": f"Invalid RSS feed: {feed.bozo_exception}",
                "data": []
            }
        
        # Informations sur le flux
        feed_info = {
            "title": feed.feed.get("title", "Unknown"),
            "url": rss_url,
            "description": feed.feed.get("description", ""),
            "link": feed.feed.get("link", ""),
            "language": feed.feed.get("language", "")
        }
        
        # Entrées
        entries = []
        for entry in feed.entries[:limit]:
            entries.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", "")[:500],  # Limiter à 500 chars
                "published": entry.get("published", ""),
                "author": entry.get("author", "")
            })
        
        return {
            "success": True,
            "feed_info": feed_info,
            "entries": entries,
            "total_entries": len(entries)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": []
        }

# ==================== Routes ====================

@router.post("/parse")
def parse_rss(rss_url: str, limit: int = 20):
    """Parser un flux RSS et afficher le contenu"""
    try:
        result = parse_rss_feed(rss_url, limit)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "feed_info": result["feed_info"],
            "entries": result["entries"],
            "total_entries": result["total_entries"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/scrape-rss")
def scrape_rss_feed(rss_url: str, limit: int = 20):
    """Scraper un flux RSS et sauvegarder les entrées"""
    try:
        result = parse_rss_feed(rss_url, limit)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Sauvegarder chaque entrée
        feed_info = result["feed_info"]
        entries = result["entries"]
        
        documents = []
        for i, entry in enumerate(entries):
            document = {
                "url": entry["link"],
                "source_type": "rss",
                "source_name": feed_info["title"],
                "rss_feed_url": rss_url,
                "title": entry["title"],
                "summary": entry["summary"],
                "published": entry["published"],
                "author": entry["author"],
                "data": [
                    {"index": 1, "value": entry["title"]},
                    {"index": 2, "value": entry["summary"]}
                ],
                "content_type": "rss",
                "scraped_at": datetime.now(UTC)
            }
            inserted = scraped_collection.insert_one(document)
            document["_id"] = str(inserted.inserted_id)
            documents.append(document)
        
        return {
            "feed_info": feed_info,
            "scraped_entries": len(documents),
            "documents": documents
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/add-source")
def add_rss_source(request: RSSSourceCreate):
    """Ajouter une source RSS à la base de données"""
    try:
        # Valider le flux RSS
        result = parse_rss_feed(request.rss_url, limit=1)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=f"Invalid RSS feed: {result['error']}")
        
        # Créer la source
        source_doc = {
            "name": request.name,
            "url": request.rss_url,
            "source_type": "rss",
            "frequency": request.frequency,
            "limit": request.limit,
            "description": request.description or result["feed_info"]["description"],
            "active": request.active,
            "created_at": datetime.now(UTC),
            "last_scraped": None,
            "scrape_count": 0
        }
        
        inserted = sources_collection.insert_one(source_doc)
        source_doc["id"] = str(inserted.inserted_id)
        
        return {
            "message": "RSS source added successfully",
            "source": source_doc
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/sources")
def get_rss_sources():
    """Obtenir toutes les sources RSS"""
    try:
        sources = list(sources_collection.find({"source_type": "rss"}))
        
        return {
            "total": len(sources),
            "sources": [
                {
                    "id": str(source["_id"]),
                    **{k: v for k, v in source.items() if k != "_id"}
                }
                for source in sources
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/source/{source_id}/latest")
def get_rss_source_latest(source_id: str, limit: int = 10):
    """Obtenir les dernières entrées d'une source RSS"""
    try:
        source = sources_collection.find_one({"_id": ObjectId(source_id), "source_type": "rss"})
        if not source:
            raise HTTPException(status_code=404, detail="RSS source not found")
        
        # Récupérer les derniers documents scrappés de cette source
        docs = list(
            scraped_collection.find(
                {"source_name": source["name"], "source_type": "rss"}
            )
            .sort("scraped_at", -1)
            .limit(limit)
        )
        
        return {
            "source": {
                "id": str(source["_id"]),
                "name": source["name"],
                "url": source["url"]
            },
            "entries": [
                {
                    "id": str(doc["_id"]),
                    "title": doc.get("title", ""),
                    "summary": doc.get("summary", ""),
                    "published": doc.get("published", ""),
                    "author": doc.get("author", ""),
                    "scraped_at": doc.get("scraped_at")
                }
                for doc in docs
            ],
            "total": len(docs)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/refresh/{source_id}")
def refresh_rss_source(source_id: str):
    """Rafraîchir une source RSS manuellement"""
    try:
        source = sources_collection.find_one({"_id": ObjectId(source_id), "source_type": "rss"})
        if not source:
            raise HTTPException(status_code=404, detail="RSS source not found")
        
        # Parser et scraper
        result = parse_rss_feed(source["url"], source.get("limit", 20))
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Sauvegarder les entrées
        entries = result["entries"]
        documents = []
        
        for entry in entries:
            document = {
                "url": entry["link"],
                "source_type": "rss",
                "source_name": source["name"],
                "rss_feed_url": source["url"],
                "title": entry["title"],
                "summary": entry["summary"],
                "published": entry["published"],
                "author": entry["author"],
                "data": [
                    {"index": 1, "value": entry["title"]},
                    {"index": 2, "value": entry["summary"]}
                ],
                "content_type": "rss",
                "scraped_at": datetime.now(UTC)
            }
            inserted = scraped_collection.insert_one(document)
            documents.append(str(inserted.inserted_id))
        
        # Mettre à jour la source
        sources_collection.update_one(
            {"_id": ObjectId(source_id)},
            {
                "$set": {"last_scraped": datetime.now(UTC)},
                "$inc": {"scrape_count": 1}
            }
        )
        
        return {
            "message": f"RSS source refreshed: {len(documents)} new entries",
            "source_name": source["name"],
            "entries_scraped": len(documents),
            "document_ids": documents
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
