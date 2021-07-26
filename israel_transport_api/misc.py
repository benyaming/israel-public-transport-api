import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from httpx import AsyncClient
from motor.core import AgnosticDatabase, AgnosticClient
from odmantic import AIOEngine

from israel_transport_api.config import SCHED_HOURS, SCHED_MINS


scheduler = AsyncIOScheduler()
daily_trigger = CronTrigger(hour=SCHED_HOURS, minute=SCHED_MINS, timezone=pytz.timezone('Asia/Jerusalem'))

motor_client: AgnosticClient
db_engine: AIOEngine
db: AgnosticDatabase

http_client = AsyncClient()
