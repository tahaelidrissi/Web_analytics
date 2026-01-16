from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Optional
import requests
from bs4 import BeautifulSoup
import io
from pypdf import PdfReader
from db import collection as scraped_collection, sources_collection, db
from datetime import datetime, UTC
from bson import ObjectId

router = APIRouter()

# ==================== Models ====================

class ScrapeRequest(BaseModel):
    """Modèle pour scraper une URL manuelle"""
    url: str
    selector: Optional[str] = None
    limit: int = 10
    
    model_config = ConfigDict(from_attributes=True)

class ScrapeBySourceRequest(BaseModel):
    """Modèle pour scraper depuis une source"""
    source_id: str
    limit: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

# ==================== Helper Functions ====================

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

def scrape_url(url: str, selector: Optional[str] = None, limit: int = 10, timeout: int = 15) -> dict:
    """Scraper une URL et retourner les données extraites"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=timeout, headers=headers)
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Invalid URL: {response.status_code}",
                "status_code": 400,
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
                "status_code": 415,
                "data": []
            }

        return {
            "success": True,
            "data": data,
            "content_type": content_type,
            "count": len(data)
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timeout",
            "status_code": 408,
            "data": []
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Request error: {str(e)}",
            "status_code": 400,
            "data": []
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status_code": 500,
            "data": []
        }

# ==================== Routes ====================

@router.post("/scrape")
def scrape_manual(request: ScrapeRequest):
    """Scraper une URL manuellement"""
    try:
        config = get_config()
        result = scrape_url(
            url=request.url,
            selector=request.selector,
            limit=min(request.limit, config["max_hits_per_source"]),
            timeout=config["timeout"]
        )

        if not result["success"]:
            status_code = result.get("status_code", 500)
            raise HTTPException(status_code=status_code, detail=result.get("error"))

        # Stockage dans MongoDB
        document = {
            "url": request.url,
            "selector": request.selector,
            "limit": request.limit,
            "count": result["count"],
            "data": result["data"],
            "content_type": result["content_type"],
            "source_id": None,
            "scraped_at": datetime.now(UTC)
        }
        inserted_doc = scraped_collection.insert_one(document)
        document["_id"] = str(inserted_doc.inserted_id)

        return document

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/scrape-source")
def scrape_by_source(request: ScrapeBySourceRequest):
    """Scraper depuis une source enregistrée"""
    try:
        # Récupérer la source
        source = sources_collection.find_one({"_id": ObjectId(request.source_id)})
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")

        if not source.get("active"):
            raise HTTPException(status_code=400, detail="Source is inactive")

        config = get_config()
        limit = min(request.limit or source.get("limit", 10), config["max_hits_per_source"])

        # Scraper l'URL
        result = scrape_url(
            url=source["url"],
            selector=source.get("selector"),
            limit=limit,
            timeout=config["timeout"]
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error"))

        # Stockage dans MongoDB
        document = {
            "url": source["url"],
            "selector": source.get("selector"),
            "source_id": ObjectId(request.source_id),
            "source_name": source.get("name"),
            "source_type": source.get("source_type"),
            "limit": limit,
            "count": result["count"],
            "data": result["data"],
            "content_type": result["content_type"],
            "scraped_at": datetime.now(UTC)
        }
        inserted_doc = collection.insert_one(document)

        # Mettre à jour la source : last_scraped et scrape_count
        sources_collection.update_one(
            {"_id": ObjectId(request.source_id)},
            {
                "$set": {"last_scraped": datetime.now(UTC)},
                "$inc": {"scrape_count": 1}
            }
        )

        # Convertir les ObjectId en string pour la réponse
        document["_id"] = str(inserted_doc.inserted_id)
        document["source_id"] = str(document["source_id"])
        return document

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/sources-status")
def get_sources_scrape_status():
    """Obtenir le statut de scrape de toutes les sources"""
    try:
        sources = list(sources_collection.find({"active": True}))
        
        status = []
        for source in sources:
            status.append({
                "source_id": str(source["_id"]),
                "name": source["name"],
                "url": source["url"],
                "last_scraped": source.get("last_scraped"),
                "scrape_count": source.get("scrape_count", 0),
                "frequency": source.get("frequency", 24),
                "next_scrape": source.get("last_scraped") if source.get("last_scraped") else None
            })
        
        return {
            "total_active_sources": len(status),
            "sources": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

