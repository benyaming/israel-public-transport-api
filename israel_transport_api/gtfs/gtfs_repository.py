from typing import List

import pymongo
from pymongo import IndexModel

from israel_transport_api import misc
from israel_transport_api.gtfs.models import Stop


async def init_db():
    id_index = IndexModel('stop_id', unique=True)
    geosphere_index = IndexModel([('location', pymongo.GEOSPHERE)])
    await misc.db['stops'].create_indexes([id_index, geosphere_index])


async def save_stops(stops: List[Stop]):
    await misc.db_engine.save_all(stops)


async def find_stop_by_id():
    ...


async def find_stops_in_area(lat: float, lng: float, radius: int):
    ...
