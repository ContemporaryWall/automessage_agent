# src/main.py
from apscheduler.schedulers.blocking import BlockingScheduler
from src.agent import run_daily_briefing
from src.config import settings
import structlog

logger = structlog.get_logger()

def main():
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(
        run_daily_briefing,
        'cron',
        hour=settings.SCHEDULE_HOUR,
        minute=settings.SCHEDULE_MINUTE,
        id='daily_briefing'
    )
    logger.info("Scheduler started", schedule=f"{settings.SCHEDULE_HOUR}:{settings.SCHEDULE_MINUTE}")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    main()