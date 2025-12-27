from fastapi import APIRouter, HTTPException
from models import ScrapeRequest
import requests
from bs4 import BeautifulSoup
import io
import PyPDF2

router = APIRouter()

@router.post("/scrape")
def scrape(request: ScrapeRequest):
    try:
        # Télécharger le contenu de l'URL
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
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            lines = text.splitlines()[:request.limit]
            data = [{"index": i+1, "value": line} for i, line in enumerate(lines)]

        # Autres types non supportés
        else:
            raise HTTPException(status_code=415, detail=f"Unsupported content type: {content_type}")

        return {
            "url": request.url,
            "selector": request.selector,
            "limit": request.limit,
            "count": len(data),
            "data": data,
            "content_type": content_type
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
