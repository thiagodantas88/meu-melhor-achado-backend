from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    id         = Column(Integer, primary_key=True, index=True)
    slug       = Column(String, unique=True, index=True)
    name       = Column(String)
    description= Column(Text)
    icon       = Column(String)
    color      = Column(String, default="#1E3A5F")
    articles   = relationship("Article", back_populates="category")

class Article(Base):
    __tablename__ = "articles"

    id              = Column(Integer, primary_key=True, index=True)
    slug            = Column(String, unique=True, index=True)
    title           = Column(String)
    summary         = Column(Text)
    category_id     = Column(Integer, ForeignKey("categories.id"))
    published_at    = Column(DateTime, default=datetime.utcnow)
    reading_time    = Column(Integer, default=5)
    image_url       = Column(String, nullable=True)
    content_sections= Column(JSON, default=list)
    is_auto         = Column(Boolean, default=False)  # gerado pelo robô
    is_offer        = Column(Boolean, default=False)  # aparece na página /ofertas
    is_featured     = Column(Boolean, default=False)  # aparece na barra principal
    active          = Column(Boolean, default=True)

    category = relationship("Category", back_populates="articles")
    products = relationship("Product", back_populates="article", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"

    id            = Column(Integer, primary_key=True, index=True)
    article_id    = Column(Integer, ForeignKey("articles.id"))
    name          = Column(String)
    summary       = Column(Text)
    pros          = Column(JSON, default=list)
    cons          = Column(JSON, default=list)
    affiliate_url = Column(String)
    image_url     = Column(String, nullable=True)
    price         = Column(String, nullable=True)
    original_price= Column(String, nullable=True)   # preço antes do desconto
    discount_pct  = Column(Float, nullable=True)     # % de desconto
    badge         = Column(String, nullable=True)
    store         = Column(String, default="amazon") # amazon | magalu
    in_stock      = Column(Boolean, default=True)
    created_at    = Column(DateTime, default=datetime.utcnow)

    article = relationship("Article", back_populates="products")
