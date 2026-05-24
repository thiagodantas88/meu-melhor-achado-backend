from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Deal
from app.rate_limit import limiter
from app.services.affiliate_links import is_product_affiliate_url

router = APIRouter(prefix="/offers", tags=["offers"])


def serialize_deal(deal: Deal):
    return {
        "id": deal.id,
        "productName": deal.product_name,
        "originalPrice": deal.original_price,
        "dealPrice": deal.deal_price,
        "discountPct": deal.discount_pct if (deal.discount_pct and deal.discount_pct > 0) else None,
        "affiliateUrl": deal.affiliate_url,
        "source": deal.source,
        "category": deal.category,
        "imageUrl": deal.image_url,
    }


@router.get("/")
@limiter.limit("60/minute")
def list_offers(
    request: Request,
    category: str = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Deal).filter(Deal.is_active == True).order_by(desc(Deal.discount_pct))
    if category:
        query = query.filter(Deal.category == category)
    deals = query.limit(limit * 3).all()
    valid_deals = [deal for deal in deals if is_product_affiliate_url(deal.affiliate_url)]
    return [serialize_deal(deal) for deal in valid_deals[:limit]]


@router.get("/products")
@limiter.limit("60/minute")
def list_offer_products(
    request: Request,
    category: str = Query(None),
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Deal).filter(Deal.is_active == True).order_by(desc(Deal.discount_pct))
    if category:
        query = query.filter(Deal.category == category)
    deals = query.limit(limit * 3).all()
    valid_deals = [deal for deal in deals if is_product_affiliate_url(deal.affiliate_url)]
    return [serialize_deal(deal) for deal in valid_deals[:limit]]
