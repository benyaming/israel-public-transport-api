import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


scheduler = AsyncIOScheduler()
daily_trigger = CronTrigger(hour=3, minute=0, timezone=pytz.timezone('Asia/Jerusalem'))
