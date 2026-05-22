from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Deal

router = APIRouter(prefix="/deals", tags=["deals"])


def serialize_deal(deal: Deal):
    return {
        "id": deal.id,
        "productName": deal.product_name,
        "originalPrice": deal.original_price,
        "dealPrice": deal.deal_price,
        "discountPct": deal.discount_pct,
        "affiliateUrl": deal.affiliate_url,
        "source": deal.source,
        "category": deal.category,
        "imageUrl": deal.image_url,
    }


@router.get("/")
def list_deals(category: str = Query(None), limit: int = Query(20), db: Session = Depends(get_db)):
    query = db.query(Deal).filter(Deal.is_active == True).order_by(desc(Deal.discount_pct))
    if category:
        query = query.filter(Deal.category == category)
    return [serialize_deal(deal) for deal in query.limit(limit).all()]
