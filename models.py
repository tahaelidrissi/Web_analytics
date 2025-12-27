from pydantic import BaseModel

class ScrapeRequest(BaseModel):
    url: str
    selector: str
    limit: int = 10
