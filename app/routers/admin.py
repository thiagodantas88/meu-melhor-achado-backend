import os
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Article, Category, DailyComparison, PriceHistory, ScraperLog
from app.services.affiliate_links import resolve_product_search_links
from app.services.scraper import SEARCH_TERMS, run_category_terms, run_daily_job

router = APIRouter(prefix="/admin", tags=["admin"])
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")


class ManualScraperRequest(BaseModel):
    mode: Literal["general", "category", "product", "reference"] = "general"
    category: Optional[str] = None
    term: Optional[str] = None


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


@router.get("/offers-history")
def get_offers_history(
    date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    category: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_key),
):
    query = db.query(PriceHistory)
    if date:
        query = query.filter(func.date(PriceHistory.recorded_at) == date)
    if category:
        query = query.filter(PriceHistory.category == category)
    if source:
        query = query.filter(PriceHistory.source == source)

    rows = query.order_by(desc(PriceHistory.recorded_at)).limit(limit).all()
    return [
        {
            "id": row.id,
            "productName": row.product_name,
            "price": row.price,
            "source": row.source,
            "category": row.category,
            "affiliateUrl": row.affiliate_url,
            "recordedAt": row.recorded_at.isoformat() if row.recorded_at else None,
            "scraperRun": row.scraper_run,
        }
        for row in rows
    ]


@router.get("/articles-history")
def get_articles_history(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_key),
):
    articles = (
        db.query(Article)
        .join(Category, Article.category_id == Category.id)
        .filter(Article.is_active == True)
        .order_by(desc(Article.published_at))
        .limit(limit)
        .all()
    )
    return [
        {
            "id": article.id,
            "slug": article.slug,
            "title": article.title,
            "category": article.category.slug if article.category else None,
            "categoryName": article.category.name if article.category else None,
            "publishedAt": article.published_at.isoformat() if article.published_at else None,
            "readingTime": article.reading_time,
            "isFeatured": article.is_featured,
            "isAuto": article.is_auto,
            "isOffer": article.is_offer,
        }
        for article in articles
    ]


@router.get("/comparisons-history")
def get_comparisons_history(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_key),
):
    comparisons = (
        db.query(DailyComparison)
        .order_by(desc(DailyComparison.created_at))
        .limit(limit)
        .all()
    )
    return [
        {
            "id": comparison.id,
            "title": comparison.title,
            "category": comparison.category,
            "date": comparison.date,
            "publishedAt": comparison.created_at.isoformat() if comparison.created_at else None,
            "summary": comparison.summary,
            "verdict": comparison.verdict,
            "criteria": comparison.criteria,
        }
        for comparison in comparisons
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


@router.post("/run-manual")
def run_manual_scraper(
    payload: ManualScraperRequest,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_key),
):
    if payload.mode == "general":
        run_daily_job(db)
        return {"status": "ok", "mode": payload.mode}

    if payload.mode == "category":
        if not payload.category:
            raise HTTPException(status_code=400, detail="Categoria obrigatoria")

        terms = [term for category, term in SEARCH_TERMS if category == payload.category]
        if not terms:
            raise HTTPException(status_code=404, detail="Categoria sem termos cadastrados")

        result = run_category_terms(db, category=payload.category, terms=terms)
        return {"status": "ok", "mode": payload.mode, **result}

    if payload.mode in {"product", "reference"}:
        if not payload.category or not payload.term:
            raise HTTPException(status_code=400, detail="Categoria e termo sao obrigatorios")

        result = run_category_terms(db, category=payload.category, terms=[payload.term])
        return {"status": "ok", "mode": payload.mode, **result}

    raise HTTPException(status_code=400, detail="Modo invalido")


@router.post("/run-category-scraper")
def run_category_scraper(
    category: str = Query(..., min_length=2),
    term: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_key),
):
    result = run_category_terms(db, category=category, terms=[term])
    return {"status": "ok", **result}
