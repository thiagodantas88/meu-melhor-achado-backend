import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.config import settings
from app.migrations import ensure_database_schema
from app.rate_limit import limiter
from app.routers import admin, articles, categories, comparisons, deals, mobilia, offers
from app.scheduler import start_scheduler
from app.seed import seed

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_database_schema()
    if settings.AUTO_SEED_ON_START:
        seed()
    scheduler = start_scheduler()
    yield
    if scheduler:
        scheduler.shutdown()


app = FastAPI(
    title="Meu Melhor Achado API",
    version="2.0.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(articles.router)
app.include_router(admin.router)
app.include_router(categories.router)
app.include_router(comparisons.router)
app.include_router(deals.router)
app.include_router(mobilia.router)
app.include_router(offers.router)


@app.get("/")
def root():
    return {"status": "ok", "project": "Meu Melhor Achado API", "version": "2.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
