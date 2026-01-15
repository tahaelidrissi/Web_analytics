from fastapi import APIRouter, HTTPException
from models import ScrapeRequest
import requests
from bs4 import BeautifulSoup
import io
from pypdf import PdfReader
from db import collection
from datetime import datetime, UTC

router = APIRouter()

@router.post("/scrape")
def scrape(request: ScrapeRequest):
    try:
        response = requests.get(request.url, timeout=15)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid URL")

        content_type = response.headers.get("Content-Type", "").lower()
        data = []

        # HTML / XML
        if "html" in content_type or "xml" in content_type:
            soup = BeautifulSoup(response.text, "html.parser")
            elements = soup.select(request.selector)[:request.limit]
            data = [{"index": i+1, "value": el.get_text(strip=True)} for i, el in enumerate(elements)]

        # TXT / CSV
        elif "text" in content_type:
            lines = response.text.splitlines()[:request.limit]
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
            lines = text.splitlines()[:request.limit]
            data = [{"index": i+1, "value": line} for i, line in enumerate(lines)]

        else:
            raise HTTPException(status_code=415, detail=f"Unsupported content type: {content_type}")

        # Stockage dans MongoDB
        document = {
            "url": request.url,
            "selector": request.selector,
            "limit": request.limit,
            "count": len(data),
            "data": data,
            "content_type": content_type,
            "scraped_at": datetime.now(UTC)
        }
        inserted_doc = collection.insert_one(document)
        document["_id"] = str(inserted_doc.inserted_id)  # Conversion ObjectId -> string

        return document

    except Exception as e:
        # Affiche l'erreur complète pour debug
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
