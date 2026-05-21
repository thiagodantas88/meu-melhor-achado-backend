from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.database import get_db
from app.models import Article
from app.schemas import ArticleOut, ArticleListOut

router = APIRouter(prefix="/articles", tags=["articles"])

@router.get("/", response_model=List[ArticleListOut])
def list_articles(
    category: Optional[str] = None,
    featured: Optional[bool] = None,
    offers: Optional[bool] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    q = db.query(Article).options(joinedload(Article.category)).filter(Article.active == True)
    if category:
        q = q.join(Article.category).filter_by(slug=category)
    if featured is not None:
        q = q.filter(Article.is_featured == featured)
    if offers is not None:
        q = q.filter(Article.is_offer == offers)
    return q.order_by(Article.published_at.desc()).limit(limit).all()

@router.get("/featured", response_model=List[ArticleListOut])
def get_featured(db: Session = Depends(get_db)):
    return (
        db.query(Article)
        .options(joinedload(Article.category))
        .filter(Article.active == True, Article.is_featured == True)
        .order_by(Article.published_at.desc())
        .limit(3)
        .all()
    )

@router.get("/recent", response_model=List[ArticleListOut])
def get_recent(db: Session = Depends(get_db)):
    return (
        db.query(Article)
        .options(joinedload(Article.category))
        .filter(Article.active == True, Article.is_featured == False)
        .order_by(Article.published_at.desc())
        .limit(6)
        .all()
    )

@router.get("/{slug}", response_model=ArticleOut)
def get_article(slug: str, db: Session = Depends(get_db)):
    article = (
        db.query(Article)
        .options(joinedload(Article.category), joinedload(Article.products))
        .filter(Article.slug == slug, Article.active == True)
        .first()
    )
    if not article:
        raise HTTPException(status_code=404, detail="Artigo não encontrado")
    return article
