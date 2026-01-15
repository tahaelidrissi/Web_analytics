from fastapi import FastAPI
from routes.scrape import router as scrape_router
from routes.sources import router as sources_router

app = FastAPI(title="Web Crawler API", version="1.0.0")

# Inclure les routes
app.include_router(scrape_router)
app.include_router(sources_router)
