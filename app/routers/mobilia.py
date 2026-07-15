import base64
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import MobiliaOffer, MobiliaSearch
from app.rate_limit import limiter
from app.services.mobilia_search import (
    build_query,
    now_filename_suffix,
    offers_to_csv,
    offers_to_xlsx,
    search_mobilia_offers,
)

router = APIRouter(prefix="/mobilia", tags=["mobilia"])
DEFAULT_CEP = "59091-130"


class MobiliaLoginRequest(BaseModel):
    email: str
    password: str


class MobiliaSearchRequest(BaseModel):
    productName: Optional[str] = ""
    productModel: Optional[str] = ""
    productType: Optional[str] = ""
    description: Optional[str] = ""
    cep: str = DEFAULT_CEP


def verify_credentials(email: str, password: str) -> None:
    if not (
        secrets.compare_digest(email, settings.MOBILIA_USER)
        and secrets.compare_digest(password, settings.MOBILIA_PASSWORD)
    ):
        raise HTTPException(status_code=401, detail="Login invalido")


def decode_basic_auth(authorization: Optional[str]) -> tuple[str, str]:
    if not authorization or not authorization.startswith("Basic "):
        raise HTTPException(status_code=401, detail="Autenticacao obrigatoria")

    try:
        raw = base64.b64decode(authorization.removeprefix("Basic ").strip()).decode("utf-8")
        email, password = raw.split(":", 1)
    except Exception:
        raise HTTPException(status_code=401, detail="Autenticacao invalida")

    return email, password


def require_mobilia_auth(authorization: Optional[str] = Header(default=None)):
    email, password = decode_basic_auth(authorization)
    verify_credentials(email, password)
    return email


def serialize_offer(offer: MobiliaOffer):
    return {
        "id": offer.id,
        "title": offer.title,
        "price": offer.price,
        "originalPrice": offer.original_price,
        "discountPct": offer.discount_pct,
        "source": offer.source,
        "sourceType": offer.source_type,
        "url": offer.url,
        "imageUrl": offer.image_url,
        "couponCode": offer.coupon_code,
        "couponNote": offer.coupon_note,
        "shippingNote": offer.shipping_note,
        "isPartner": offer.is_partner,
        "createdAt": offer.created_at.isoformat() if offer.created_at else None,
    }


def serialize_search(search: MobiliaSearch, include_offers: bool = False):
    data = {
        "id": search.id,
        "productName": search.product_name,
        "productModel": search.product_model,
        "productType": search.product_type,
        "description": search.description,
        "query": search.query,
        "cep": search.cep,
        "resultsCount": search.results_count,
        "createdAt": search.created_at.isoformat() if search.created_at else None,
    }
    if include_offers:
        data["offers"] = [serialize_offer(offer) for offer in search.offers]
    return data


def export_rows(searches: list[MobiliaSearch]) -> list[dict]:
    rows = []
    for search in searches:
        for offer in search.offers:
            rows.append(
                {
                    "data": search.created_at.isoformat() if search.created_at else "",
                    "busca": search.query,
                    "titulo": offer.title,
                    "preco": offer.price if offer.price is not None else "",
                    "preco_original": offer.original_price if offer.original_price is not None else "",
                    "desconto_pct": offer.discount_pct if offer.discount_pct is not None else "",
                    "loja": offer.source,
                    "parceiro": "sim" if offer.is_partner else "nao",
                    "cupom": offer.coupon_code or "",
                    "observacao_cupom": offer.coupon_note or "",
                    "frete": offer.shipping_note or "",
                    "url": offer.url or "",
                    "imagem": offer.image_url or "",
                }
            )
    return rows


@router.post("/login")
@limiter.limit("20/minute")
def login(payload: MobiliaLoginRequest, request: Request):
    verify_credentials(payload.email, payload.password)
    return {"status": "ok"}


@router.post("/search")
@limiter.limit("10/minute")
def search(
    payload: MobiliaSearchRequest,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(require_mobilia_auth),
):
    query = build_query(
        payload.productName or "",
        payload.productModel or "",
        payload.productType or "",
        payload.description or "",
    )
    if not query:
        raise HTTPException(status_code=400, detail="Preencha pelo menos um campo para iniciar a busca")

    offers = search_mobilia_offers(query, payload.cep or DEFAULT_CEP)
    search_row = MobiliaSearch(
        product_name=payload.productName or None,
        product_model=payload.productModel or None,
        product_type=payload.productType or None,
        description=payload.description or None,
        query=query,
        cep=payload.cep or DEFAULT_CEP,
        results_count=len(offers),
    )
    db.add(search_row)
    db.flush()

    for offer in offers:
        db.add(
            MobiliaOffer(
                search_id=search_row.id,
                title=offer["title"],
                price=offer.get("price"),
                original_price=offer.get("original_price"),
                discount_pct=offer.get("discount_pct"),
                source=offer["source"],
                source_type=offer.get("source_type") or "marketplace",
                url=offer.get("url"),
                image_url=offer.get("image_url"),
                coupon_code=offer.get("coupon_code"),
                coupon_note=offer.get("coupon_note"),
                shipping_note=offer.get("shipping_note"),
                is_partner=bool(offer.get("is_partner")),
            )
        )

    db.commit()
    db.refresh(search_row)
    return serialize_search(search_row, include_offers=True)


@router.get("/history")
@limiter.limit("30/minute")
def history(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: str = Depends(require_mobilia_auth),
):
    searches = db.query(MobiliaSearch).order_by(desc(MobiliaSearch.created_at)).limit(limit).all()
    return [serialize_search(search, include_offers=True) for search in searches]


@router.get("/export.csv")
@limiter.limit("10/minute")
def export_csv(
    request: Request,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: str = Depends(require_mobilia_auth),
):
    searches = db.query(MobiliaSearch).order_by(desc(MobiliaSearch.created_at)).limit(limit).all()
    content = offers_to_csv(export_rows(searches))
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="mobilia-ofertas-{now_filename_suffix()}.csv"'},
    )


@router.get("/export.xlsx")
@limiter.limit("10/minute")
def export_xlsx(
    request: Request,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: str = Depends(require_mobilia_auth),
):
    searches = db.query(MobiliaSearch).order_by(desc(MobiliaSearch.created_at)).limit(limit).all()
    content = offers_to_xlsx(export_rows(searches))
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="mobilia-ofertas-{now_filename_suffix()}.xlsx"'},
    )
