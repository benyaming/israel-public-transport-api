import csv
import logging
import pathlib
from collections import defaultdict

from psycopg import AsyncConnection
from psycopg.types import TypeInfo
from psycopg.types.shapely import register_shapely
from shapely.geometry import Point

from israel_transport_api.gtfs.utils import parse_route_long_name, parse_stop_description
from israel_transport_api.gtfs.repository.routes_repository import invalidate_route_cache


GTFS_FP = pathlib.Path(__file__).parent.parent.parent.parent / 'gtfs_data'


logger = logging.getLogger(__name__)


async def load_agencies(conn: AsyncConnection, force_load: bool = False):
    logger.info('Loading agencies...')

    if not force_load and (await (await conn.execute('SELECT COUNT(*) FROM agencies')).fetchone())[0] > 0:
        logger.info('Agencies already loaded.')
        return

    fp = GTFS_FP / 'agency.txt'
    if not fp.exists():
        logger.error('Agency file not found!')
        return

    rows = []

    with open(fp, 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        for line in reader:
            rows.append(line)

    async with conn.cursor() as acur:
        await acur.execute('CREATE TEMP TABLE tmp_agency (LIKE agencies INCLUDING DEFAULTS) ON COMMIT DROP')

        insert_query = '''
            COPY tmp_agency (
                id, name, url, timezone, lang, phone
            ) FROM STDIN
        '''

        async with acur.copy(insert_query) as acopy:
            for row in rows:
                await acopy.write_row(row[:-1])

        update_query = '''
            INSERT INTO agencies 
            SELECT * FROM tmp_agency 
            ON CONFLICT (id) DO UPDATE
            SET 
                id = EXCLUDED.id,
                name = EXCLUDED.name,
                url = EXCLUDED.url,
                timezone = EXCLUDED.timezone,
                lang = EXCLUDED.lang,
                phone = EXCLUDED.phone
        '''
        await acur.execute(update_query)

    await conn.commit()
    logger.info('Agencies loaded.')


async def load_stops(conn: AsyncConnection, force_load: bool = False):
    logger.info('Loading stops...')

    if not force_load and (await (await conn.execute('SELECT COUNT(*) FROM stops')).fetchone())[0] > 0:
        logger.info('Stops already loaded.')
        return

    fp = GTFS_FP / 'stops.txt'
    if not fp.exists():
        logger.error('Stops file not found!')
        return

    with open(fp, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)  # skip headers

        stops = []
        for row in reader:
            try:
                street, city, platform, floor = parse_stop_description(row[3]) if row[3] else [None] * 4
            except (ValueError, IndexError):
                msg = f'Failed to parse stop description. Row: {row}'
                logger.exception(msg)
                continue

            stops.append([
                int(row[0]),
                city,
                int(row[1]),
                floor,
                Point(float(row[4]), float(row[5])),
                int(row[6]) or 0,
                row[2],
                row[7] or None,
                platform,
                street,
                row[8] or None
            ])

    info = await TypeInfo.fetch(conn, "geography")
    register_shapely(info, conn)

    async with conn.cursor() as acur:
        await acur.execute('CREATE TEMP TABLE tmp_stop (LIKE stops INCLUDING DEFAULTS) ON COMMIT DROP')

        insert_query = '''
            COPY tmp_stop (
                id, city, code, floor, location, location_type, name, parent_station_id, 
                platform, street, zone_id
            ) FROM STDIN
        '''

        async with acur.copy(insert_query) as acopy:
            for stop in stops:
                await acopy.write_row(stop)

        update_query = '''
            INSERT INTO stops 
            SELECT * FROM tmp_stop 
            ON CONFLICT (id) DO UPDATE
            SET 
                id = EXCLUDED.id,
                city = EXCLUDED.city,
                floor = EXCLUDED.floor,
                location = EXCLUDED.location,
                location_type = EXCLUDED.location_type,
                name = EXCLUDED.name,
                parent_station_id = EXCLUDED.parent_station_id,
                platform = EXCLUDED.platform,
                street = EXCLUDED.street,
                zone_id = EXCLUDED.zone_id
        '''
        await acur.execute(update_query)

    await conn.commit()
    logger.info('Stops loaded.')


async def load_routes(conn: AsyncConnection, force_load: bool = False):
    logger.info('Loading routes...')

    if not force_load and (await (await conn.execute('SELECT COUNT(*) FROM routes')).fetchone())[0] > 0:
        logger.info('Routes already loaded.')
        await invalidate_route_cache(conn)
        return

    fp = GTFS_FP / 'routes.txt'
    if not fp.exists():
        logger.error('File routes.txt not found!')

    with open(fp, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)  # skip headers
        routes = []

        for row in reader:
            try:
                from_stop_name, from_city, to_stop_name, to_city = parse_route_long_name(row[3])
            except (ValueError, IndexError):
                msg = f'Failed to parse route long name. Row: {row}'
                logger.exception(msg)
                continue

            routes.append([
                row[0],
                row[1],
                row[2],
                from_stop_name,
                to_stop_name,
                from_city,
                to_city,
                row[4],
                row[5],
                row[6]
            ])

    async with conn.cursor() as acur:
        await acur.execute('CREATE TEMP TABLE tmp_route (LIKE routes INCLUDING DEFAULTS) ON COMMIT DROP')

        insert_query = '''
            COPY tmp_route (
                id, agency_id, short_name, from_stop_name, to_stop_name, from_city, to_city, description, type, color
            ) FROM STDIN
        '''

        async with acur.copy(insert_query) as acopy:
            for route in routes:
                await acopy.write_row(route)

        update_query = '''
            INSERT INTO routes 
            SELECT * FROM tmp_route 
            ON CONFLICT (id) DO UPDATE
            SET 
                id = EXCLUDED.id,
                agency_id = EXCLUDED.agency_id,
                short_name = EXCLUDED.short_name,
                from_stop_name = EXCLUDED.from_stop_name,
                to_stop_name = EXCLUDED.to_stop_name,
                from_city = EXCLUDED.from_city,
                to_city = EXCLUDED.to_city,
                description = EXCLUDED.description,
                type = EXCLUDED.type,
                color = EXCLUDED.color
        '''

        await acur.execute(update_query)

    await conn.commit()
    logger.info('Routes loaded.')

    await invalidate_route_cache(conn)


async def load_routes_for_stop(conn: AsyncConnection, force_load: bool = False):
    logger.info('Loading routes for stop...')

    if not force_load and (await (await conn.execute('SELECT COUNT(*) FROM routes_for_stop')).fetchone())[0] > 0:
        logger.info('Routes for stop already loaded.')
        return

    # Create a dictionary to hold stop_id to stop_code mapping
    stop_id_to_code = {}

    with open(GTFS_FP / 'stops.txt', mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            stop_id = row[0]
            stop_code = row[1]
            stop_id_to_code[stop_id] = stop_code

    # Create a dictionary to hold trip_id to route_id mapping
    trip_to_route = {}

    with open(GTFS_FP / 'trips.txt', mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)

        for row in reader:
            trip_id = row[2]
            route_id = row[0]
            trip_to_route[trip_id] = route_id

    # Create a dictionary to hold the stop code to routes mapping using defaultdict
    stop_routes_dict = defaultdict(set)

    with open(GTFS_FP / 'stop_times.txt', mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)

        for row in reader:
            stop_id = row[3]
            trip_id = row[0]
            route_id = trip_to_route[trip_id]

            # Convert stop_id to stop_code
            stop_code = stop_id_to_code.get(stop_id, None)
            if stop_code:
                stop_routes_dict[stop_code].add(route_id)

    stop_routes_dict = {stop_code: list(routes) for stop_code, routes in stop_routes_dict.items()}

    await conn.execute('CREATE TEMP TABLE tmp_routes_for_stop (LIKE routes_for_stop INCLUDING DEFAULTS) ON COMMIT DROP')

    insert_query = '''
        COPY tmp_routes_for_stop (stop_code, route_ids)
        FROM STDIN
    '''

    async with conn.cursor() as acur:
        async with acur.copy(insert_query) as acopy:
            for stop_code, route_ids in stop_routes_dict.items():
                await acopy.write_row((stop_code, route_ids))

        update_query = '''
            INSERT INTO routes_for_stop
            SELECT * FROM tmp_routes_for_stop
            ON CONFLICT (stop_code) DO UPDATE
            SET route_ids = EXCLUDED.route_ids
        '''

        await acur.execute(update_query)

    await conn.commit()
    logger.info('Routes for stop loaded.')
