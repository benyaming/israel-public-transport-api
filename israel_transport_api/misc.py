import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from httpx import AsyncClient

from israel_transport_api.config import env


scheduler = AsyncIOScheduler()
daily_trigger = CronTrigger(hour=env.SCHED_HOURS, minute=env.SCHED_MINS, timezone=pytz.timezone('Asia/Jerusalem'))

http_client = AsyncClient(timeout=3.0)
