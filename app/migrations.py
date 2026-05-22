from sqlalchemy import inspect, text

from app.database import Base, engine


def _table_columns(table_name: str) -> set[str]:
    inspector = inspect(engine)
    if not inspector.has_table(table_name):
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def _add_column_if_missing(table_name: str, column_name: str, ddl: str) -> None:
    if column_name in _table_columns(table_name):
        return
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl}"))


def ensure_database_schema() -> None:
    """Create new tables and add the small set of columns needed by v2.

    Railway already has a v1 database. SQLAlchemy create_all creates missing
    tables but does not alter existing ones, so these additive migrations keep
    the deploy compatible without wiping production data.
    """
    Base.metadata.create_all(bind=engine)

    article_columns = _table_columns("articles")
    if article_columns:
        _add_column_if_missing("articles", "is_active", "BOOLEAN DEFAULT TRUE")
        _add_column_if_missing("articles", "is_featured", "BOOLEAN DEFAULT FALSE")
        _add_column_if_missing("articles", "is_offer", "BOOLEAN DEFAULT FALSE")
        _add_column_if_missing("articles", "is_auto", "BOOLEAN DEFAULT FALSE")
        _add_column_if_missing("articles", "active", "BOOLEAN DEFAULT TRUE")
        _add_column_if_missing("articles", "content_sections", "JSON")

        with engine.begin() as conn:
            refreshed_columns = _table_columns("articles")
            if {"active", "is_active"}.issubset(refreshed_columns):
                conn.execute(text("UPDATE articles SET is_active = active WHERE is_active IS NULL"))

    product_columns = _table_columns("products")
    if product_columns:
        _add_column_if_missing("products", "source", "VARCHAR(50) DEFAULT 'amazon'")
        _add_column_if_missing("products", "store", "VARCHAR DEFAULT 'amazon'")
        _add_column_if_missing("products", "original_price", "VARCHAR")
        _add_column_if_missing("products", "discount_pct", "FLOAT")
        _add_column_if_missing("products", "in_stock", "BOOLEAN DEFAULT TRUE")
        _add_column_if_missing("products", "created_at", "TIMESTAMP")

        with engine.begin() as conn:
            refreshed_columns = _table_columns("products")
            if {"store", "source"}.issubset(refreshed_columns):
                conn.execute(text("UPDATE products SET source = store WHERE source IS NULL AND store IS NOT NULL"))
