from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.exchange.service import scheduled_update_rates

scheduler = AsyncIOScheduler()

def setup_scheduler():
    scheduler.add_job(
        scheduled_update_rates,
        IntervalTrigger(hours=6),
        id="update_exchange_rates",
        replace_existing=True,
    )