import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import events, admin

logging.basicConfig(level=settings.log_level)

app = FastAPI(title="Goiânia Cultural API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "goiania-cultural-api"}
