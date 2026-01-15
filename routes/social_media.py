from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import requests
from db import collection as scraped_collection, sources_collection, db
from datetime import datetime, UTC
from bson import ObjectId
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/social", tags=["social_media"])

# ==================== Models ====================

class SocialMediaPost(BaseModel):
    """Un post de réseau social"""
    platform: str  # twitter, instagram, facebook, linkedin
    post_id: str
    author: str
    content: str
    likes: int = 0
    shares: int = 0
    comments: int = 0
    posted_at: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class SocialMediaSourceCreate(BaseModel):
    """Créer une source de réseau social"""
    name: str
    platform: str  # twitter, instagram, facebook, linkedin
    handle_or_id: str  # @username ou ID
    api_key: Optional[str] = None  # Pour les APIs
    frequency: int = 6  # heures entre les scrapes
    limit: int = 20  # nombre de posts à récupérer
    description: Optional[str] = None
    active: bool = True
    
    model_config = ConfigDict(from_attributes=True)

class TwitterSearchParams(BaseModel):
    """Paramètres pour recherche Twitter"""
    query: str
    limit: int = 10
    language: str = "en"
    
    model_config = ConfigDict(from_attributes=True)

# ==================== Helper Functions ====================

def fetch_twitter_data(handle: str, limit: int = 20) -> dict:
    """Récupérer les données Twitter via une API publique"""
    try:
        # Utiliser une API publique pour Twitter (example: Twitter API v2)
        # Pour cette démo, on utilise une approche simple
        logger.info(f"Fetching Twitter data for handle: {handle}")
        
        # Note: Nécessite une clé API Twitter valide
        # Ceci est un exemple simplifié
        return {
            "success": True,
            "platform": "twitter",
            "handle": handle,
            "posts": [],
            "count": 0,
            "message": "Twitter API integration requires valid credentials"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "platform": "twitter"
        }

def fetch_instagram_data(username: str, limit: int = 20) -> dict:
    """Récupérer les données Instagram"""
    try:
        # Note: Nécessite des credentials Instagram valides
        logger.info(f"Fetching Instagram data for user: {username}")
        
        return {
            "success": True,
            "platform": "instagram",
            "username": username,
            "posts": [],
            "count": 0,
            "message": "Instagram API integration requires valid credentials"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "platform": "instagram"
        }

def fetch_facebook_data(page_id: str, limit: int = 20) -> dict:
    """Récupérer les données Facebook"""
    try:
        logger.info(f"Fetching Facebook data for page: {page_id}")
        
        return {
            "success": True,
            "platform": "facebook",
            "page_id": page_id,
            "posts": [],
            "count": 0,
            "message": "Facebook API integration requires valid credentials"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "platform": "facebook"
        }

def fetch_linkedin_data(profile_id: str, limit: int = 20) -> dict:
    """Récupérer les données LinkedIn"""
    try:
        logger.info(f"Fetching LinkedIn data for profile: {profile_id}")
        
        return {
            "success": True,
            "platform": "linkedin",
            "profile_id": profile_id,
            "posts": [],
            "count": 0,
            "message": "LinkedIn API integration requires valid credentials"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "platform": "linkedin"
        }

# ==================== Routes ====================

@router.post("/add-source")
def add_social_media_source(request: SocialMediaSourceCreate):
    """Ajouter une source de réseau social"""
    try:
        # Valider la plateforme
        valid_platforms = ["twitter", "instagram", "facebook", "linkedin"]
        if request.platform.lower() not in valid_platforms:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform. Supported: {', '.join(valid_platforms)}"
            )
        
        # Créer la source
        source_doc = {
            "name": request.name,
            "url": f"{request.platform}://{request.handle_or_id}",
            "source_type": "social_media",
            "platform": request.platform.lower(),
            "handle_or_id": request.handle_or_id,
            "frequency": request.frequency,
            "limit": request.limit,
            "description": request.description or f"{request.platform} account",
            "active": request.active,
            "created_at": datetime.now(UTC),
            "last_scraped": None,
            "scrape_count": 0
        }
        
        # Ne pas sauvegarder les clés API en plain text
        if request.api_key:
            source_doc["has_api_key"] = True
        
        inserted = sources_collection.insert_one(source_doc)
        source_doc["id"] = str(inserted.inserted_id)
        
        return {
            "message": f"{request.platform.upper()} source added successfully",
            "source": {
                "id": source_doc["id"],
                "name": source_doc["name"],
                "platform": source_doc["platform"],
                "handle_or_id": source_doc["handle_or_id"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/sources")
def get_social_media_sources(platform: Optional[str] = None):
    """Obtenir les sources de réseaux sociaux"""
    try:
        query = {"source_type": "social_media"}
        if platform:
            query["platform"] = platform.lower()
        
        sources = list(sources_collection.find(query))
        
        return {
            "total": len(sources),
            "platform_filter": platform,
            "sources": [
                {
                    "id": str(source["_id"]),
                    "name": source["name"],
                    "platform": source["platform"],
                    "handle_or_id": source["handle_or_id"],
                    "last_scraped": source.get("last_scraped"),
                    "scrape_count": source.get("scrape_count", 0)
                }
                for source in sources
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/test-connection/{source_id}")
def test_social_media_connection(source_id: str):
    """Tester la connexion à une source de réseau social"""
    try:
        source = sources_collection.find_one({
            "_id": ObjectId(source_id),
            "source_type": "social_media"
        })
        
        if not source:
            raise HTTPException(status_code=404, detail="Social media source not found")
        
        platform = source.get("platform", "").lower()
        handle = source.get("handle_or_id")
        
        # Tester selon la plateforme
        if platform == "twitter":
            result = fetch_twitter_data(handle, limit=1)
        elif platform == "instagram":
            result = fetch_instagram_data(handle, limit=1)
        elif platform == "facebook":
            result = fetch_facebook_data(handle, limit=1)
        elif platform == "linkedin":
            result = fetch_linkedin_data(handle, limit=1)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
        
        if result["success"]:
            return {
                "status": "connected",
                "platform": platform,
                "message": result.get("message", "Connection successful")
            }
        else:
            return {
                "status": "failed",
                "platform": platform,
                "error": result.get("error")
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/scrape/{source_id}")
def scrape_social_media_source(source_id: str):
    """Scraper une source de réseau social"""
    try:
        source = sources_collection.find_one({
            "_id": ObjectId(source_id),
            "source_type": "social_media"
        })
        
        if not source:
            raise HTTPException(status_code=404, detail="Social media source not found")
        
        if not source.get("active"):
            raise HTTPException(status_code=400, detail="Source is inactive")
        
        platform = source.get("platform", "").lower()
        handle = source.get("handle_or_id")
        limit = source.get("limit", 20)
        
        # Récupérer les données selon la plateforme
        if platform == "twitter":
            result = fetch_twitter_data(handle, limit)
        elif platform == "instagram":
            result = fetch_instagram_data(handle, limit)
        elif platform == "facebook":
            result = fetch_facebook_data(handle, limit)
        elif platform == "linkedin":
            result = fetch_linkedin_data(handle, limit)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        # Sauvegarder les données
        posts = result.get("posts", [])
        documents = []
        
        for post in posts:
            document = {
                "url": source.get("url"),
                "source_type": "social_media",
                "platform": platform,
                "source_name": source.get("name"),
                "handle_or_id": handle,
                "post_id": post.get("id"),
                "author": post.get("author", handle),
                "content": post.get("content", post.get("text", "")),
                "likes": post.get("likes", 0),
                "shares": post.get("shares", 0),
                "comments": post.get("comments", 0),
                "posted_at": post.get("posted_at"),
                "data": [
                    {"index": 1, "value": post.get("content", post.get("text", ""))}
                ],
                "content_type": "social_media",
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
            "message": f"Successfully scraped {platform} source",
            "platform": platform,
            "source_name": source.get("name"),
            "posts_scraped": len(documents),
            "document_ids": documents
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/source/{source_id}/posts")
def get_social_media_posts(source_id: str, limit: int = 20):
    """Obtenir les posts scrappés d'une source"""
    try:
        source = sources_collection.find_one({
            "_id": ObjectId(source_id),
            "source_type": "social_media"
        })
        
        if not source:
            raise HTTPException(status_code=404, detail="Social media source not found")
        
        # Récupérer les documents scrappés
        docs = list(
            scraped_collection.find(
                {"platform": source.get("platform"), "source_name": source.get("name")}
            )
            .sort("scraped_at", -1)
            .limit(limit)
        )
        
        return {
            "source": {
                "id": str(source["_id"]),
                "name": source["name"],
                "platform": source["platform"]
            },
            "posts": [
                {
                    "id": str(doc["_id"]),
                    "author": doc.get("author"),
                    "content": doc.get("content"),
                    "likes": doc.get("likes", 0),
                    "shares": doc.get("shares", 0),
                    "comments": doc.get("comments", 0),
                    "posted_at": doc.get("posted_at"),
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

@router.get("/stats")
def get_social_media_stats():
    """Obtenir les statistiques des réseaux sociaux"""
    try:
        # Compter les sources par plateforme
        platforms = ["twitter", "instagram", "facebook", "linkedin"]
        stats = {}
        
        for platform in platforms:
            count = sources_collection.count_documents({
                "source_type": "social_media",
                "platform": platform,
                "active": True
            })
            posts_count = scraped_collection.count_documents({
                "source_type": "social_media",
                "platform": platform
            })
            stats[platform] = {
                "sources": count,
                "posts_scraped": posts_count
            }
        
        total_sources = sources_collection.count_documents({"source_type": "social_media"})
        total_posts = scraped_collection.count_documents({"source_type": "social_media"})
        
        return {
            "total_sources": total_sources,
            "total_posts_scraped": total_posts,
            "by_platform": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
