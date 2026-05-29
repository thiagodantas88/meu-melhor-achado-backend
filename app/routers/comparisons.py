from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DailyComparison
from app.rate_limit import limiter

router = APIRouter(prefix="/comparisons", tags=["comparisons"])
PROJECT_TZ = ZoneInfo("America/Fortaleza")


def sanitize_product(product):
    if not isinstance(product, dict):
        return product

    sanitized = dict(product)
    pros = sanitized.get("pros")
    if isinstance(pros, list):
        sanitized["pros"] = [
            "Produto selecionado" if pro == "0% de desconto" else pro
            for pro in pros
        ]
    return sanitized


def serialize_comparison(comparison: DailyComparison):
    return {
        "id": comparison.id,
        "title": comparison.title,
        "productA": sanitize_product(comparison.product_a),
        "productB": sanitize_product(comparison.product_b),
        "summary": comparison.summary,
        "verdict": comparison.verdict,
        "criteria": comparison.criteria,
        "category": comparison.category,
        "date": comparison.date,
        "publishedAt": comparison.created_at.isoformat() if comparison.created_at else None,
    }


@router.get("/today")
@limiter.limit("60/minute")
def get_today(request: Request, db: Session = Depends(get_db)):
    today = datetime.now(PROJECT_TZ).strftime("%Y-%m-%d")
    items = (
        db.query(DailyComparison)
        .filter(DailyComparison.date == today)
        .order_by(desc(DailyComparison.created_at))
        .limit(3)
        .all()
    )
    return [serialize_comparison(item) for item in items]


@router.get("/")
@limiter.limit("60/minute")
def list_comparisons(request: Request, limit: int = Query(9, ge=1, le=100), db: Session = Depends(get_db)):
    items = (
        db.query(DailyComparison)
        .order_by(desc(DailyComparison.created_at))
        .limit(limit)
        .all()
    )
    return [serialize_comparison(item) for item in items]
