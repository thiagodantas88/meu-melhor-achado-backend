from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ScraperLog

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/scraper-logs")
def get_scraper_logs(limit: int = Query(20), db: Session = Depends(get_db)):
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
