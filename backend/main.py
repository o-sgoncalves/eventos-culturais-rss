import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from config import settings
from routers import events, admin

logging.basicConfig(level=settings.log_level)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Goiânia Cultural API", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
