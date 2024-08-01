import csv
import logging
import pathlib

from psycopg import AsyncConnection
from psycopg.types import TypeInfo
from psycopg.types.shapely import register_shapely
from shapely.geometry import Point

from israel_transport_api.config import env
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
        await acur.execute(
            'CREATE TEMP TABLE tmp_agency (LIKE agencies INCLUDING DEFAULTS) ON COMMIT DROP'
        )

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
        await acur.execute(
            'CREATE TEMP TABLE tmp_stop (LIKE stops INCLUDING DEFAULTS) ON COMMIT DROP'
        )

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
        await acur.execute(
            'CREATE TEMP TABLE tmp_route (LIKE routes INCLUDING DEFAULTS) ON COMMIT DROP'
        )

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


async def load_trips(conn: AsyncConnection, force_load: bool = False):
    logger.info('Loading trips...')

    if not force_load and (await (await conn.execute('SELECT COUNT(*) FROM trips')).fetchone())[0] > 0:
        logger.info('Trips already loaded.')
        return

    fp = GTFS_FP / 'trips.txt'
    if not fp.exists():
        logger.error('File trips.txt not found!')

    with open(fp, 'r') as file:
        reader = csv.reader(file)
        next(reader, None)

        trips = []

        for row in reader:
            trips.append([
                int(row[2]),
                int(row[0]),
                int(row[1]),
                row[3],
                int(row[4])
            ])

    async with conn.cursor() as acur:
        await acur.execute(
            'CREATE TEMP TABLE tmp_trip (LIKE trips INCLUDING DEFAULTS) ON COMMIT DROP'
        )

        insert_query = '''
            COPY tmp_trip (
                id, route_id, service_id, headsign, direction_id
            ) FROM STDIN
        '''

        async with acur.copy(insert_query) as acopy:
            for trip in trips:
                await acopy.write_row(trip)

        update_query = '''
            INSERT INTO trips 
            SELECT * FROM tmp_trip 
            ON CONFLICT (id) DO UPDATE
            SET 
                id = EXCLUDED.id,
                route_id = EXCLUDED.route_id,
                service_id = EXCLUDED.service_id,
                headsign = EXCLUDED.headsign,
                direction_id = EXCLUDED.direction_id
        '''

        await acur.execute(update_query)

    await conn.commit()
    logger.info('Trips loaded.')


async def load_stop_times(conn: AsyncConnection, force_load: bool = False):
    logger.info('Loading stop times...')

    if not force_load and (await (await conn.execute('SELECT COUNT(*) FROM stop_times')).fetchone())[0] > 0:
        logger.info('Stop times already loaded.')
        return

    fp = GTFS_FP / 'stop_times.txt'
    if not fp.exists():
        logger.error('File stop_times.txt not found!')

    async def insert_batch(batch: list):
        async with conn.cursor() as acur:
            insert_query = '''
                COPY tmp_stop_time (
                    trip_id, stop_id, stop_sequence
                ) FROM STDIN
            '''
            async with acur.copy(insert_query) as acopy:
                for stop_time in batch:
                    await acopy.write_row(stop_time)

            update_query = '''
                INSERT INTO stop_times 
                SELECT tmp_stop_time.* FROM tmp_stop_time 
                JOIN stops ON tmp_stop_time.stop_id = stops.id
                JOIN trips ON tmp_stop_time.trip_id = trips.id
                ON CONFLICT (trip_id, stop_id, stop_sequence) DO UPDATE
                SET 
                    trip_id = EXCLUDED.trip_id,
                    stop_id = EXCLUDED.stop_id,
                    stop_sequence = EXCLUDED.stop_sequence
            '''
            await acur.execute(update_query)

    async with conn.cursor() as acur:
        await acur.execute(
            'CREATE TEMP TABLE tmp_stop_time (LIKE stop_times INCLUDING DEFAULTS) ON COMMIT DROP'
        )

    current_batch = 1

    with open(fp, 'r') as file:
        reader = csv.reader(file)
        next(reader, None)

        stop_times = []
        for i, row in enumerate(reader):
            stop_times.append([int(row[0]), int(row[3]), int(row[4])])

            if len(stop_times) >= env.DB_BATCH_SIZE:
                logger.info(f'Inserting butch #{current_batch}')
                await insert_batch(stop_times)
                current_batch += 1
                stop_times = []

        if stop_times:
            logger.info(f'Inserting butch #{current_batch}')
            await insert_batch(stop_times)

    await conn.commit()
    logger.info('Stop times loaded.')
