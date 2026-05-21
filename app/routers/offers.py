from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models import Article, Product
from app.schemas import ArticleListOut, ProductOut

router = APIRouter(prefix="/offers", tags=["offers"])

@router.get("/", response_model=List[ArticleListOut])
def list_offers(limit: int = 20, db: Session = Depends(get_db)):
    """Retorna artigos marcados como oferta para a página /ofertas."""
    return (
        db.query(Article)
        .options(joinedload(Article.category))
        .filter(Article.active == True, Article.is_offer == True)
        .order_by(Article.published_at.desc())
        .limit(limit)
        .all()
    )

@router.get("/products", response_model=List[ProductOut])
def list_offer_products(limit: int = 30, db: Session = Depends(get_db)):
    """Retorna produtos com desconto para exibição direta na página /ofertas."""
    return (
        db.query(Product)
        .join(Article)
        .filter(
            Article.active == True,
            Article.is_offer == True,
            Product.discount_pct != None,
            Product.in_stock == True,
        )
        .order_by(Product.discount_pct.desc())
        .limit(limit)
        .all()
    )
