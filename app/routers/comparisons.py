from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DailyComparison

router = APIRouter(prefix="/comparisons", tags=["comparisons"])


def serialize_comparison(comparison: DailyComparison):
    return {
        "id": comparison.id,
        "title": comparison.title,
        "productA": comparison.product_a,
        "productB": comparison.product_b,
        "summary": comparison.summary,
        "category": comparison.category,
        "date": comparison.date,
    }


@router.get("/today")
def get_today(db: Session = Depends(get_db)):
    today = date.today().strftime("%Y-%m-%d")
    items = (
        db.query(DailyComparison)
        .filter(DailyComparison.date == today)
        .order_by(desc(DailyComparison.created_at))
        .limit(3)
        .all()
    )
    return [serialize_comparison(item) for item in items]


@router.get("/")
def list_comparisons(limit: int = Query(9), db: Session = Depends(get_db)):
    items = (
        db.query(DailyComparison)
        .order_by(desc(DailyComparison.created_at))
        .limit(limit)
        .all()
    )
    return [serialize_comparison(item) for item in items]
