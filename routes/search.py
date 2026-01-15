from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from db import collection as scraped_collection, db
from datetime import datetime, UTC
from bson import ObjectId
import re

router = APIRouter(prefix="/search", tags=["search"])

# ==================== Models ====================

class SearchQuery(BaseModel):
    """Modèle pour une requête de recherche"""
    keywords: List[str]  # Mots-clés à rechercher
    case_sensitive: bool = False
    exact_match: bool = False  # Recherche exacte ou contient
    limit: int = 50
    skip: int = 0
    source_id: Optional[str] = None  # Filtrer par source spécifique
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class SearchResult(BaseModel):
    """Un résultat de recherche"""
    id: str
    url: str
    source_id: Optional[str]
    content: str
    matched_keywords: List[str]
    scraped_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SearchResponse(BaseModel):
    """Réponse de recherche"""
    total: int
    results: List[SearchResult]
    query: SearchQuery

# ==================== Routes ====================

def build_search_regex(keywords: List[str], case_sensitive: bool = False):
    """Construire une regex pour la recherche"""
    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = '|'.join(re.escape(kw) for kw in keywords)
    return re.compile(pattern, flags)

@router.post("/", response_model=SearchResponse)
def search_documents(query: SearchQuery):
    """Rechercher dans les documents scrappés par keywords"""
    try:
        # Construire le filtre MongoDB
        mongo_filter = {}
        
        # Filtrer par source si spécifié
        if query.source_id:
            try:
                mongo_filter["source_id"] = ObjectId(query.source_id)
            except:
                mongo_filter["source_id"] = query.source_id
        
        # Filtrer par date
        if query.start_date or query.end_date:
            date_filter = {}
            if query.start_date:
                date_filter["$gte"] = query.start_date
            if query.end_date:
                date_filter["$lte"] = query.end_date
            mongo_filter["scraped_at"] = date_filter
        
        # Compter le total
        total = scraped_collection.count_documents(mongo_filter)
        
        # Récupérer les documents
        documents = list(
            scraped_collection
            .find(mongo_filter)
            .skip(query.skip)
            .limit(query.limit)
            .sort("scraped_at", -1)
        )
        
        # Construire la regex
        search_regex = build_search_regex(query.keywords, query.case_sensitive)
        
        # Filtrer et formater les résultats
        results = []
        for doc in documents:
            matched_keywords = []
            content_text = ""
            
            # Extraire le contenu
            if "data" in doc and isinstance(doc["data"], list):
                content_text = " ".join([str(item.get("value", "")) for item in doc["data"]])
            elif "content" in doc:
                content_text = doc["content"]
            
            # Chercher les keywords
            if query.exact_match:
                # Recherche exacte
                if query.case_sensitive:
                    matched = [kw for kw in query.keywords if kw in content_text]
                else:
                    matched = [
                        kw for kw in query.keywords 
                        if kw.lower() in content_text.lower()
                    ]
            else:
                # Recherche contient (regex)
                matched = search_regex.findall(content_text)
                matched = list(set(matched))  # Déduplicater
            
            if matched:
                results.append(SearchResult(
                    id=str(doc["_id"]),
                    url=doc.get("url", ""),
                    source_id=str(doc.get("source_id")) if doc.get("source_id") else None,
                    content=content_text[:500],  # Limiter à 500 caractères
                    matched_keywords=matched,
                    scraped_at=doc.get("scraped_at", datetime.now(UTC))
                ))
        
        return SearchResponse(
            total=total,
            results=results,
            query=query
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error searching: {str(e)}")

@router.get("/keywords", response_model=dict)
def get_top_keywords(limit: int = 20):
    """Obtenir les keywords les plus fréquents dans les documents"""
    try:
        # Récupérer tous les documents
        documents = list(scraped_collection.find({}))
        
        keyword_count = {}
        
        for doc in documents:
            # Extraire le contenu
            content_text = ""
            if "data" in doc and isinstance(doc["data"], list):
                content_text = " ".join([str(item.get("value", "")) for item in doc["data"]])
            elif "content" in doc:
                content_text = doc["content"]
            
            # Extraire les mots (simple tokenization)
            words = re.findall(r'\b[a-zA-Z]{3,}\b', content_text.lower())
            for word in words:
                keyword_count[word] = keyword_count.get(word, 0) + 1
        
        # Trier et retourner les top keywords
        top_keywords = sorted(
            keyword_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return {
            "total_unique_keywords": len(keyword_count),
            "top_keywords": [{"keyword": kw, "count": count} for kw, count in top_keywords]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting keywords: {str(e)}")

@router.post("/advanced", response_model=SearchResponse)
def advanced_search(query: SearchQuery):
    """Recherche avancée avec plusieurs options"""
    return search_documents(query)
