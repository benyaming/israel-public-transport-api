from typing import List

import pymongo
from pymongo import IndexModel

from israel_transport_api import misc
from israel_transport_api.gtfs.exceptions import StopNotFound
from israel_transport_api.gtfs.models import Stop, Route


async def init_db():
    id_index = IndexModel('stop_id', unique=True)
    geosphere_index = IndexModel([('location', pymongo.GEOSPHERE)])
    await misc.db['stops'].create_indexes([id_index, geosphere_index])


async def save_stops(stops: List[dict]):
    for stop in stops:
        await misc.motor_client.gtfs.stops.update_one({'_id': stop['_id']}, {'$set': stop}, upsert=True)


async def find_stop_by_id(stop_id: int) -> Stop:
    stop = await misc.db_engine.find_one(Stop, Stop.id == stop_id)
    if not stop:
        raise StopNotFound(stop_id)
    return stop


async def find_stop_by_code(stop_code: int) -> Stop:
    stop = await misc.db_engine.find_one(Stop, Stop.code == stop_code)
    if not stop:
        raise StopNotFound(stop_code)
    return stop


async def find_stops_in_area(lat: float, lng: float, distance: int) -> List[Stop]:
    radians = (distance / 1000) / 6371
    query = {
        'location': {
            '$geoWithin': {
                '$centerSphere': [(lat, lng), radians]
            }
        }
    }
    result = await misc.db_engine.find(Stop, query)
    return result


async def get_stops_count() -> int:
    return await misc.db_engine.count(Stop)

