import asyncio
from typing import Dict

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from motor.core import AgnosticDatabase, AgnosticCollection, AgnosticClient
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from israel_transport_api.config import DB_URL, DB_NAME
from israel_transport_api.gtfs.models import Route


ROUTES_STORE: Dict[str, Route] = {}

scheduler = AsyncIOScheduler()
daily_trigger = CronTrigger(hour=3, minute=0, timezone=pytz.timezone('Asia/Jerusalem'))

motor_client: AgnosticClient
db_engine: AIOEngine
db: AgnosticDatabase
