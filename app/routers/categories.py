from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/")
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.get("/{slug}")
def get_category(slug: str, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.slug == slug).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return category
