from typing import Dict

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiopg.pool import Pool

from israel_transport_api.gtfs.models import Route

scheduler = AsyncIOScheduler()
daily_trigger = CronTrigger(hour=3, minute=0, timezone=pytz.timezone('Asia/Jerusalem'))
pool: Pool

ROUTES_STORE: Dict[str, Route] = {}
