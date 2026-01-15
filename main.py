from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes.scrape import router as scrape_router
from routes.sources import router as sources_router
from routes.config import router as config_router
from routes.search import router as search_router
from routes.scheduler_routes import router as scheduler_router
from routes.rss import router as rss_router
from routes.social_media import router as social_media_router
from scheduler import start_scheduler, stop_scheduler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan context manager pour les événements de démarrage/arrêt
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    logger.info("🚀 Starting Web Crawler API...")
    start_scheduler()
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Web Crawler API...")
    stop_scheduler()

app = FastAPI(
    title="Web Crawler API",
    version="1.0.0",
    lifespan=lifespan
)

# Inclure les routes
app.include_router(scrape_router)
app.include_router(sources_router)
app.include_router(config_router)
app.include_router(search_router)
app.include_router(scheduler_router)
app.include_router(rss_router)
app.include_router(social_media_router)

@app.get("/health")
async def health_check():
    """Vérification de santé de l'API"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "message": "Web Crawler API is running"
    }
