import os
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import text
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DailyComparison, ScraperLog
from app.services.affiliate_links import resolve_product_search_links
from app.services.scraper import run_daily_job

router = APIRouter(prefix="/admin", tags=["admin"])
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")


def verify_admin_key(x_api_key: Optional[str] = Header(default=None, alias="X-Api-Key")):
    if not ADMIN_API_KEY or x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Nao autorizado")
    return x_api_key


@router.get("/scraper-logs")
def get_scraper_logs(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_key),
):
    logs = (
        db.query(ScraperLog)
        .order_by(desc(ScraperLog.started_at))
        .limit(limit)
        .all()
    )
    return [
        {
            "runId": log.run_id,
            "startedAt": log.started_at.isoformat() if log.started_at else None,
            "finishedAt": log.finished_at.isoformat() if log.finished_at else None,
            "dealsFound": log.deals_found,
            "dealsPublished": log.deals_published,
            "dealsFallback": log.deals_fallback,
            "amazonFound": log.amazon_found,
            "magaluFound": log.magalu_found,
            "errors": log.errors,
            "status": log.status,
            "notes": log.notes,
        }
        for log in logs
    ]


@router.post("/resolve-affiliate-links")
def resolve_affiliate_links(
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_key),
):
    updated = resolve_product_search_links(db, limit=limit)
    return {"updated": updated, "limit": limit}


@router.get("/database-encoding")
def get_database_encoding(
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_key),
):
    encoding = db.execute(text("SHOW SERVER_ENCODING")).scalar()
    return {"serverEncoding": encoding}


@router.post("/clear-comparisons")
def clear_comparisons(
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_key),
):
    deleted = db.query(DailyComparison).delete()
    db.commit()
    return {"deleted": deleted}


@router.post("/run-scraper")
def run_scraper(
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_key),
):
    run_daily_job(db)
    return {"status": "ok"}
