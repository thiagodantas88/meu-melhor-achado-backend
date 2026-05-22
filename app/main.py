import logging
import threading
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import SessionLocal
from app.migrations import ensure_database_schema
from app.routers import articles, categories, comparisons, deals, offers
from app.scheduler import start_scheduler
from app.seed import seed
from app.services.scraper import run_daily_job

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

manual_job_status = {
    "state": "pending",
    "startedAt": None,
    "finishedAt": None,
    "error": None,
}


def run_daily_job_once_on_startup():
    manual_job_status.update(
        {
            "state": "running",
            "startedAt": datetime.utcnow().isoformat(),
            "finishedAt": None,
            "error": None,
        }
    )
    db = SessionLocal()
    try:
        run_daily_job(db)
        manual_job_status.update({"state": "completed", "finishedAt": datetime.utcnow().isoformat()})
    except Exception as exc:
        logger.exception("Erro ao executar robo manual no startup")
        manual_job_status.update(
            {
                "state": "failed",
                "finishedAt": datetime.utcnow().isoformat(),
                "error": str(exc),
            }
        )
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_database_schema()
    if settings.AUTO_SEED_ON_START:
        seed()
    scheduler = start_scheduler()
    threading.Thread(target=run_daily_job_once_on_startup, daemon=True).start()
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


@app.get("/internal/manual-job-status")
def get_manual_job_status():
    return manual_job_status
