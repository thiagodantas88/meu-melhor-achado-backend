import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.database import SessionLocal
from app.services.scraper import run_daily_job

logger = logging.getLogger(__name__)


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")

    def job():
        db = SessionLocal()
        try:
            run_daily_job(db)
        except Exception as exc:
            logger.error("Erro no job diário: %s", exc)
        finally:
            db.close()

    scheduler.add_job(
        job,
        trigger=CronTrigger(hour=6, minute=0, timezone="America/Sao_Paulo"),
        id="daily_scraper",
        replace_existing=True,
    )
    scheduler.add_job(
        job,
        trigger=CronTrigger(hour=18, minute=30, timezone="America/Sao_Paulo"),
        id="evening_scraper",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Agendador iniciado: robo roda todo dia as 06:00 (Brasilia)")
    logger.info("Segunda rodada agendada: 18:30 (Brasilia)")
    return scheduler
