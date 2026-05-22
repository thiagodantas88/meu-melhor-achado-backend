import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.migrations import ensure_database_schema
from app.routers import articles, categories, comparisons, deals, offers
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
    scheduler.shutdown()


app = FastAPI(
    title="Meu Melhor Achado API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(articles.router)
app.include_router(categories.router)
app.include_router(comparisons.router)
app.include_router(deals.router)
app.include_router(offers.router)


@app.get("/")
def root():
    return {"status": "ok", "project": "Meu Melhor Achado API", "version": "2.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
