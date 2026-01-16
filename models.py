from pydantic import BaseModel, ConfigDict

# Note: ScrapeRequest est maintenant dans routes/scrape.py
# Ce fichier peut être utilisé pour d'autres modèles globaux à l'avenir

class HealthCheck(BaseModel):
    """Modèle de vérification de santé"""
    status: str
    version: str
    
    model_config = ConfigDict(from_attributes=True)

