from fastapi import FastAPI
from routes.scrape import router as scrape_router
from routes.sources import router as sources_router
from routes.config import router as config_router
from routes.search import router as search_router

app = FastAPI(title="Web Crawler API", version="1.0.0")

# Inclure les routes
app.include_router(scrape_router)
app.include_router(sources_router)
app.include_router(config_router)
app.include_router(search_router)
