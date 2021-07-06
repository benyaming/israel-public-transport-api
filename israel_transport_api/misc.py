import asyncio
from typing import Dict

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from motor.core import AgnosticDatabase, AgnosticClient
from odmantic import AIOEngine


scheduler = AsyncIOScheduler()
daily_trigger = CronTrigger(hour=3, minute=0, timezone=pytz.timezone('Asia/Jerusalem'))

motor_client: AgnosticClient
db_engine: AIOEngine
db: AgnosticDatabase
