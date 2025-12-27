from fastapi import FastAPI
from routes.scrape import router as scrape_router

app = FastAPI()

# Inclure les routes
app.include_router(scrape_router)
