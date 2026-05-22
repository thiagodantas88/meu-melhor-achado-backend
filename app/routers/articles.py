from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Article, Category

router = APIRouter(prefix="/articles", tags=["articles"])


def serialize_article(article: Article, full: bool = False):
    data = {
        "id": article.id,
        "slug": article.slug,
        "title": article.title,
        "summary": article.summary,
        "publishedAt": article.published_at.strftime("%Y-%m-%d") if article.published_at else None,
        "readingTime": article.reading_time,
        "imageUrl": article.image_url,
        "isFeatured": article.is_featured,
        "isOffer": article.is_offer,
        "category": {
            "slug": article.category.slug,
            "name": article.category.name,
            "icon": article.category.icon,
            "color": article.category.color,
        } if article.category else None,
    }

    if full:
        if not article.sections and article.content_sections:
            data["contentSections"] = article.content_sections
        else:
            data["contentSections"] = [
                {
                    "type": section.type,
                    "text": section.text,
                    "title": section.title,
                    "items": section.items,
                }
                for section in article.sections
            ]

        data["products"] = [
            {
                "id": str(product.id),
                "name": product.name,
                "summary": product.summary,
                "pros": product.pros or [],
                "cons": product.cons or [],
                "affiliateUrl": product.affiliate_url,
                "price": product.price,
                "badge": product.badge,
                "imageUrl": product.image_url,
                "source": product.source or product.store,
            }
            for product in article.products
        ]

    return data


@router.get("/")
def list_articles(category: str = Query(None), limit: int = Query(10), db: Session = Depends(get_db)):
    query = (
        db.query(Article)
        .options(joinedload(Article.category))
        .filter(Article.is_active == True)
        .order_by(desc(Article.published_at))
    )
    if category:
        query = query.join(Category).filter(Category.slug == category)
    return [serialize_article(article) for article in query.limit(limit).all()]


@router.get("/featured")
def get_featured(db: Session = Depends(get_db)):
    articles = (
        db.query(Article)
        .options(joinedload(Article.category))
        .filter(Article.is_active == True, Article.is_featured == True)
        .order_by(desc(Article.published_at))
        .limit(3)
        .all()
    )
    return [serialize_article(article) for article in articles]


@router.get("/recent")
def get_recent(limit: int = Query(5), db: Session = Depends(get_db)):
    articles = (
        db.query(Article)
        .options(joinedload(Article.category))
        .filter(Article.is_active == True)
        .order_by(desc(Article.published_at))
        .limit(limit)
        .all()
    )
    return [serialize_article(article) for article in articles]


@router.get("/{slug}")
def get_article(slug: str, db: Session = Depends(get_db)):
    article = (
        db.query(Article)
        .options(joinedload(Article.category), joinedload(Article.sections), joinedload(Article.products))
        .filter(Article.slug == slug, Article.is_active == True)
        .first()
    )
    if not article:
        raise HTTPException(status_code=404, detail="Artigo não encontrado")
    return serialize_article(article, full=True)
