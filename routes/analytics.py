from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from db import db
from datetime import datetime, UTC
from bson import ObjectId
import os
from openai import OpenAI
import json

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==================== Models ====================

class DocumentAnalysis(BaseModel):
    """Résultat d'analyse d'un document"""
    document_id: str
    summary: str
    sentiment: str  # positive, negative, neutral
    category: str
    keywords: List[str]
    entities: List[str]
    
    model_config = ConfigDict(from_attributes=True)

class AnalyticsStats(BaseModel):
    """Statistiques analytiques"""
    total_documents: int
    sentiment_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    top_keywords: List[Dict[str, Any]]
    
    model_config = ConfigDict(from_attributes=True)

class AnalyzeRequest(BaseModel):
    """Requête d'analyse"""
    document_id: str
    
    model_config = ConfigDict(from_attributes=True)

class BatchAnalyzeRequest(BaseModel):
    """Requête d'analyse en batch"""
    limit: int = 10
    
    model_config = ConfigDict(from_attributes=True)

# ==================== Helper Functions ====================

def analyze_document_with_llm(content: str) -> dict:
    """Analyser un document avec OpenAI GPT"""
    try:
        prompt = f"""Analyse le texte suivant et fournis:
1. Un résumé en 2-3 phrases
2. Le sentiment général (positive, negative, neutral)
3. La catégorie principale (technology, business, health, entertainment, sports, politics, science, other)
4. 5 mots-clés principaux
5. Les entités nommées importantes (personnes, lieux, organisations)

Texte: {content[:2000]}

Réponds UNIQUEMENT en JSON avec ce format exact:
{{
  "summary": "résumé ici",
  "sentiment": "positive/negative/neutral",
  "category": "catégorie",
  "keywords": ["mot1", "mot2", "mot3", "mot4", "mot5"],
  "entities": ["entité1", "entité2", "entité3"]
}}"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un assistant d'analyse de texte. Réponds toujours en JSON valide."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        result = response.choices[0].message.content
        # Parser le JSON
        analysis = json.loads(result)
        return analysis
        
    except Exception as e:
        # Fallback: analyse heuristique locale sans LLM
        try:
            text = content
            # Tokens simples
            import re
            tokens = re.findall(r"\b[\w'-]{3,}\b", text.lower())
            # Compter fréquences
            from collections import Counter
            freq = Counter(tokens)
            # Stopwords basiques
            stop = set(["les","des","une","dans","avec","pour","nous","vous","elles","ils","est","sont","qui","que","quoi","donc","mais","ou","et","alors","ni","car","sur","par","entre","comme","sans","aux","chez","plus","moins","tres","bien","mal"]) 
            keywords = [w for w,_ in freq.most_common(50) if w not in stop][:5]

            # Sentiment heuristique
            positive_words = {"bon","excellent","super","heureux","positif","succès","amour","beau","génial"}
            negative_words = {"mauvais","terrible","triste","négatif","échec","haine","laid","problème"}
            pos = sum(freq[w] for w in positive_words)
            neg = sum(freq[w] for w in negative_words)
            sentiment = "neutral"
            if pos > neg:
                sentiment = "positive"
            elif neg > pos:
                sentiment = "negative"

            # Catégorie heuristique
            category_map = {
                "technology": {"tech","ai","informatique","logiciel","internet","données"},
                "business": {"entreprise","marché","finance","vente","client","produit"},
                "health": {"santé","maladie","médecin","hôpital","virus","vaccin"},
                "entertainment": {"film","musique","art","spectacle","jeu"},
                "sports": {"sport","match","football","basket","tennis","compétition"},
                "politics": {"politique","gouvernement","élection","loi","ministre","parti"},
                "science": {"science","recherche","expérience","laboratoire","physique","chimie"}
            }
            category = "other"
            for cat, words in category_map.items():
                if any(w in freq for w in words):
                    category = cat
                    break

            # Entités simples: mots capitalisés (approximatif)
            entities = list(set(re.findall(r"\b[A-Z][a-zA-Z]{2,}\b", content)))[:5]

            # Résumé simple: premières phrases
            sentences = re.split(r"(?<=[.!?])\s+", content.strip())
            summary = " ".join(sentences[:2])[:300]

            return {
                "summary": summary if summary else "Résumé non disponible",
                "sentiment": sentiment,
                "category": category,
                "keywords": keywords,
                "entities": entities
            }
        except Exception:
            return {
                "summary": "Erreur d'analyse",
                "sentiment": "neutral",
                "category": "other",
                "keywords": [],
                "entities": [],
                "error": str(e)
            }

# ==================== Routes ====================

@router.post("/analyze-document", response_model=DocumentAnalysis)
def analyze_single_document(request: AnalyzeRequest):
    """Analyser un document spécifique avec LLM"""
    try:
        scraped_collection = db["scraped_data"]
        doc = scraped_collection.find_one({"_id": ObjectId(request.document_id)})
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Extraire le contenu
        content = ""
        if "data" in doc and isinstance(doc["data"], list):
            content = " ".join([str(item.get("value", "")) for item in doc["data"]])
        elif "content" in doc:
            content = doc["content"]
        
        if not content:
            raise HTTPException(status_code=400, detail="No content to analyze")
        
        # Analyser avec LLM
        analysis = analyze_document_with_llm(content)
        
        # Sauvegarder l'analyse
        analysis_collection = db["document_analysis"]
        analysis_doc = {
            "document_id": ObjectId(request.document_id),
            "summary": analysis["summary"],
            "sentiment": analysis["sentiment"],
            "category": analysis["category"],
            "keywords": analysis["keywords"],
            "entities": analysis["entities"],
            "analyzed_at": datetime.now(UTC)
        }
        analysis_collection.update_one(
            {"document_id": ObjectId(request.document_id)},
            {"$set": analysis_doc},
            upsert=True
        )
        
        return DocumentAnalysis(
            document_id=request.document_id,
            **analysis
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@router.post("/analyze-batch")
def analyze_batch_documents(request: BatchAnalyzeRequest):
    """Analyser plusieurs documents en batch"""
    try:
        scraped_collection = db["scraped_data"]
        analysis_collection = db["document_analysis"]
        
        # Récupérer les documents non analysés
        analyzed_ids = [doc["document_id"] for doc in analysis_collection.find({}, {"document_id": 1})]
        documents = list(scraped_collection.find(
            {"_id": {"$nin": analyzed_ids}}
        ).limit(request.limit))
        
        results = []
        for doc in documents:
            # Extraire le contenu
            content = ""
            if "data" in doc and isinstance(doc["data"], list):
                content = " ".join([str(item.get("value", "")) for item in doc["data"]])
            elif "content" in doc:
                content = doc["content"]
            
            if not content:
                continue
            
            # Analyser
            analysis = analyze_document_with_llm(content)
            
            # Sauvegarder
            analysis_doc = {
                "document_id": doc["_id"],
                "summary": analysis["summary"],
                "sentiment": analysis["sentiment"],
                "category": analysis["category"],
                "keywords": analysis["keywords"],
                "entities": analysis["entities"],
                "analyzed_at": datetime.now(UTC)
            }
            analysis_collection.insert_one(analysis_doc)
            
            results.append({
                "document_id": str(doc["_id"]),
                "analysis": analysis
            })
        
        return {
            "analyzed_count": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis error: {str(e)}")

@router.get("/stats", response_model=AnalyticsStats)
def get_analytics_stats():
    """Obtenir les statistiques d'analyse"""
    try:
        analysis_collection = db["document_analysis"]
        
        # Compter total
        total = analysis_collection.count_documents({})
        
        # Distribution des sentiments
        sentiment_pipeline = [
            {"$group": {"_id": "$sentiment", "count": {"$sum": 1}}}
        ]
        sentiment_results = list(analysis_collection.aggregate(sentiment_pipeline))
        sentiment_dist = {item["_id"]: item["count"] for item in sentiment_results}
        
        # Distribution des catégories
        category_pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}}
        ]
        category_results = list(analysis_collection.aggregate(category_pipeline))
        category_dist = {item["_id"]: item["count"] for item in category_results}
        
        # Top keywords
        keyword_pipeline = [
            {"$unwind": "$keywords"},
            {"$group": {"_id": "$keywords", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 20}
        ]
        keyword_results = list(analysis_collection.aggregate(keyword_pipeline))
        top_keywords = [{"keyword": item["_id"], "count": item["count"]} for item in keyword_results]
        
        return AnalyticsStats(
            total_documents=total,
            sentiment_distribution=sentiment_dist,
            category_distribution=category_dist,
            top_keywords=top_keywords
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

@router.get("/documents-by-category/{category}")
def get_documents_by_category(category: str, limit: int = 50):
    """Récupérer les documents d'une catégorie spécifique"""
    try:
        analysis_collection = db["document_analysis"]
        scraped_collection = db["scraped_data"]
        
        # Trouver les analyses de cette catégorie
        analyses = list(analysis_collection.find({"category": category}).limit(limit))
        
        results = []
        for analysis in analyses:
            doc = scraped_collection.find_one({"_id": analysis["document_id"]})
            if doc:
                results.append({
                    "document_id": str(doc["_id"]),
                    "url": doc.get("url", ""),
                    "summary": analysis.get("summary", ""),
                    "sentiment": analysis.get("sentiment", ""),
                    "keywords": analysis.get("keywords", []),
                    "scraped_at": doc.get("scraped_at")
                })
        
        return {
            "category": category,
            "count": len(results),
            "documents": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/search-by-keywords")
def search_by_keywords(keywords: str, limit: int = 20):
    """Recherche sémantique par mots-clés extraits"""
    try:
        analysis_collection = db["document_analysis"]
        scraped_collection = db["scraped_data"]
        
        # Rechercher dans les keywords
        keyword_list = [kw.strip() for kw in keywords.split(",")]
        analyses = list(analysis_collection.find(
            {"keywords": {"$in": keyword_list}}
        ).limit(limit))
        
        results = []
        for analysis in analyses:
            doc = scraped_collection.find_one({"_id": analysis["document_id"]})
            if doc:
                results.append({
                    "document_id": str(doc["_id"]),
                    "url": doc.get("url", ""),
                    "summary": analysis.get("summary", ""),
                    "category": analysis.get("category", ""),
                    "matched_keywords": [kw for kw in analysis.get("keywords", []) if kw in keyword_list],
                    "scraped_at": doc.get("scraped_at")
                })
        
        return {
            "searched_keywords": keyword_list,
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
