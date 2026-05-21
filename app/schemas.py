from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any

class CategoryOut(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    icon: str
    color: str

    class Config:
        from_attributes = True

class ProductOut(BaseModel):
    id: int
    name: str
    summary: str
    pros: List[str]
    cons: List[str]
    affiliate_url: str
    image_url: Optional[str]
    price: Optional[str]
    original_price: Optional[str]
    discount_pct: Optional[float]
    badge: Optional[str]
    store: str
    in_stock: bool

    class Config:
        from_attributes = True

class ArticleOut(BaseModel):
    id: int
    slug: str
    title: str
    summary: str
    category: CategoryOut
    published_at: datetime
    reading_time: int
    image_url: Optional[str]
    content_sections: List[Any]
    is_auto: bool
    is_offer: bool
    is_featured: bool
    products: List[ProductOut] = []

    class Config:
        from_attributes = True

class ArticleListOut(BaseModel):
    id: int
    slug: str
    title: str
    summary: str
    category: CategoryOut
    published_at: datetime
    reading_time: int
    image_url: Optional[str]
    is_featured: bool
    is_offer: bool

    class Config:
        from_attributes = True
