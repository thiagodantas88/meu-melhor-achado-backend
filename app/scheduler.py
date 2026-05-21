from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
from app.database import SessionLocal
from app.scraper.generator import generate_daily_comparatives
import pytz

def run_daily_job():
    """Wrapper síncrono para rodar a corrotina assíncrona."""
    print("[Scheduler] Iniciando job diário...")
    db = SessionLocal()
    try:
        asyncio.run(generate_daily_comparatives(db))
    except Exception as e:
        print(f"[Scheduler] Erro no job diário: {e}")
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler(timezone=pytz.timezone("America/Sao_Paulo"))
    scheduler.add_job(
        run_daily_job,
        trigger=CronTrigger(hour=6, minute=0),  # todo dia às 6h horário de Brasília
        id="daily_comparatives",
        replace_existing=True,
    )
    scheduler.start()
    print("[Scheduler] Robô diário ativo — roda todo dia às 06:00 (Brasília)")
    return scheduler
