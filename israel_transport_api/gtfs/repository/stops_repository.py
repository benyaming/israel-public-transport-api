from psycopg.connection_async import AsyncConnection

from israel_transport_api.gtfs.exceptions import StopNotFound
from israel_transport_api.gtfs.models import Stop


async def find_stop_by_id(stop_id: int, conn: AsyncConnection) -> Stop:
    query = '''
        SELECT
            *,
            st_x(st_geomfromwkb(location)),
            st_y(st_geomfromwkb(location))
        FROM stops
        WHERE id = %s
    '''
    stop = await (await conn.cursor().execute(query, (stop_id,))).fetchone()
    if not stop:
        raise StopNotFound(stop_id)
    return Stop.from_row(stop)


async def find_stop_by_code(stop_code: int, conn: AsyncConnection) -> Stop:
    query = '''
        SELECT 
            *,
            st_x(st_geomfromwkb(location)), 
            st_y(st_geomfromwkb(location))
        FROM stops 
        WHERE code = %s
    '''
    stop = await (await conn.cursor().execute(query, (stop_code,))).fetchone()
    if not stop:
        raise StopNotFound(stop_code)
    return Stop.from_row(stop)


async def find_stops_in_area(lat: float, lng: float, distance: int, conn: AsyncConnection) -> list[Stop]:
    stops = await (await conn.cursor().execute(
        '''
            SELECT 
                *,
                st_x(st_geomfromwkb(location)), 
                st_y(st_geomfromwkb(location))
            FROM stops WHERE ST_DWithin(location, ST_MakePoint(%s, %s)::geography, %s)''',
        (lat, lng, distance)
    )).fetchall()
    return [Stop.from_row(stop) for stop in stops]


async def find_stops_by_parent_id(parent_id: int, conn: AsyncConnection) -> list[Stop]:
    stops = await (await conn.cursor().execute(
        '''
            SELECT
                *,
                st_x(st_geomfromwkb(location)),
                st_y(st_geomfromwkb(location))
            FROM stops WHERE parent_station_id = %s
            ORDER BY platform
        ''',
        (parent_id,)
    )).fetchall()
    return [Stop.from_row(stop) for stop in stops]
