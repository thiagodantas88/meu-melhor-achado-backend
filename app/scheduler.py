import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.database import SessionLocal
from app.services.scraper import run_daily_job

logger = logging.getLogger(__name__)


def start_scheduler():
    if not settings.SCRAPER_ENABLED:
        logger.info("Robo desativado via SCRAPER_ENABLED=False")
        return None

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
        trigger=CronTrigger(
            hour=settings.SCRAPER_MORNING_HOUR,
            minute=settings.SCRAPER_MORNING_MINUTE,
            timezone="America/Sao_Paulo",
        ),
        id="morning_scraper",
        replace_existing=True,
    )
    scheduler.add_job(
        job,
        trigger=CronTrigger(
            hour=settings.SCRAPER_EVENING_HOUR,
            minute=settings.SCRAPER_EVENING_MINUTE,
            timezone="America/Sao_Paulo",
        ),
        id="evening_scraper",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Robo agendado: %02d:%02d e %02d:%02d (Brasilia)",
        settings.SCRAPER_MORNING_HOUR,
        settings.SCRAPER_MORNING_MINUTE,
        settings.SCRAPER_EVENING_HOUR,
        settings.SCRAPER_EVENING_MINUTE,
    )
    return scheduler
