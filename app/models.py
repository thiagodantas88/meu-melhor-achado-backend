from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(10))
    color = Column(String(10), default="#1E3A5F")
    articles = relationship("Article", back_populates="category")

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    title = Column(String(300), nullable=False)
    summary = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id"))
    published_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    reading_time = Column(Integer, default=5)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)

    # Campos legados preservados para não quebrar a base atual nem o /offers.
    content_sections = Column(JSON, default=list)
    is_auto = Column(Boolean, default=False)
    is_offer = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    active = Column(Boolean, default=True)

    category = relationship("Category", back_populates="articles")
    products = relationship("Product", back_populates="article", cascade="all, delete-orphan")
    sections = relationship(
        "ContentSection",
        back_populates="article",
        cascade="all, delete-orphan",
        order_by="ContentSection.order",
    )

class ContentSection(Base):
    __tablename__ = "content_sections"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    type = Column(String(50))
    text = Column(Text)
    title = Column(String(300))
    items = Column(JSON)
    order = Column(Integer, default=0)
    article = relationship("Article", back_populates="sections")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=True)
    name = Column(String(300), nullable=False)
    summary = Column(Text)
    pros = Column(JSON, default=list)
    cons = Column(JSON, default=list)
    affiliate_url = Column(String)
    image_url = Column(String(500), nullable=True)
    price = Column(String(50), nullable=True)
    badge = Column(String(100), nullable=True)
    source = Column(String(50), default="amazon")

    # Campos legados/complementares usados nas telas de oferta.
    original_price = Column(String, nullable=True)
    discount_pct = Column(Float, nullable=True)
    store = Column(String, default="amazon")
    in_stock = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    article = relationship("Article", back_populates="products")

class DailyComparison(Base):
    __tablename__ = "daily_comparisons"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), nullable=False)
    title = Column(String(300))
    product_a = Column(JSON)
    product_b = Column(JSON)
    summary = Column(Text)
    category = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())

class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(300), nullable=False)
    original_price = Column(Float)
    deal_price = Column(Float)
    discount_pct = Column(Integer)
    affiliate_url = Column(String(1000))
    source = Column(String(50))
    category = Column(String(100))
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    product_name = Column(String(300), nullable=False)
    price = Column(Float, nullable=False)
    source = Column(String(50))
    category = Column(String(100))
    affiliate_url = Column(String(1000))
    recorded_at = Column(DateTime, server_default=func.now())
    scraper_run = Column(String(50))

class ScraperLog(Base):
    __tablename__ = "scraper_logs"

    id = Column(Integer, primary_key=True)
    run_id = Column(String(50))
    started_at = Column(DateTime, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)
    deals_found = Column(Integer, default=0)
    deals_published = Column(Integer, default=0)
    deals_fallback = Column(Integer, default=0)
    amazon_found = Column(Integer, default=0)
    magalu_found = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    status = Column(String(50), default="ok")
    notes = Column(Text, nullable=True)
