from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import articles, categories, offers
from app.scheduler import start_scheduler
from app.config import settings
from app.seed import seed

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria tabelas e inicia o scheduler ao subir
    Base.metadata.create_all(bind=engine)
    if settings.AUTO_SEED_ON_START:
        seed()
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()

app = FastAPI(
    title="Meu Melhor Achado — API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(articles.router)
app.include_router(categories.router)
app.include_router(offers.router)

@app.get("/")
def root():
    return {"status": "ok", "project": "Meu Melhor Achado API"}

@app.get("/health")
def health():
    return {"status": "healthy"}
