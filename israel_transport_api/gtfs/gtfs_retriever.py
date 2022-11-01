import asyncio
import csv
import ftplib
import io
import logging
import pathlib
import zipfile
from typing import TextIO

from shapely.geometry import Point

from israel_transport_api.config import env
from israel_transport_api.gtfs.exceptions import GtfsFileNotFound
from israel_transport_api.gtfs.models import Route
from israel_transport_api.gtfs.repository import stops_repository, routes_repository
from israel_transport_api.gtfs.utils import parse_route_long_name, parse_stop_description
from israel_transport_api.gtfs.repository import db_updater

GTFS_FP = pathlib.Path(__file__).parent.parent.parent / 'gtfs_data'
GTFS_FILES = [
    'agency.txt',
    'calendar.txt',
    'fare_attributes.txt',
    'fare_rules.txt',
    'routes.txt',
    'shapes.txt',
    'stop_times.txt',
    'stops.txt',
    'translations.txt',
    'trips.txt',
]

logger = logging.getLogger(__name__)


async def _download_gtfs_data_from_ftp() -> io.BytesIO:
    logger.debug(f'Trying to establish ftp connection with {env.GTFS_URL}...')

    ftp = ftplib.FTP(env.GTFS_URL)
    ftp.login()

    bio = io.BytesIO()

    logger.debug('Downloading zip file...')
    ftp.retrbinary('RETR israel-public-transportation.zip', bio.write)
    logger.debug('Done.')
    return bio


async def _download_gtfs_data():
    logger.info('Starting to update gtfs files...')
    gtfs_data_io = await _download_gtfs_data_from_ftp()

    logger.debug(f'Saving files to {GTFS_FP}...')
    with zipfile.ZipFile(gtfs_data_io) as zip_file:
        if not GTFS_FP.exists():
            GTFS_FP.mkdir()

        zip_file.extractall(GTFS_FP)
    logger.debug('Done.')


def _process_stops_file(fio: TextIO) -> list[list]:
    reader = csv.reader(fio)
    next(reader, None)  # skip headers

    stops_to_save = []
    for row in reader:
        try:
            street, city, platform, floor = parse_stop_description(row[3])
        except (ValueError, IndexError):
            msg = f'Failed to parse stop description. Row: {row}'
            # logger.exception(msg)
            continue

        stops_to_save.append([
            int(row[0]),
            int(row[1]),
            row[2],
            street,
            city,
            platform,
            floor,
            Point(float(row[4]), float(row[5])),
            row[6],
            int(row[7]) if row[7] else None,
            row[8]
        ])
    return stops_to_save


def _process_routes_file(fio: TextIO) -> list[Route]:
    reader = csv.reader(fio)
    next(reader, None)  # skip headers
    routes = []

    for row in reader:
        try:
            from_stop_name, from_city, to_stop_name, to_city = parse_route_long_name(row[3])
        except (ValueError, IndexError):
            msg = f'Failed to parse route long name. Row: {row}'
            logger.exception(msg)
            continue

        routes.append(Route(
            id=(row[0]),
            agency_id=row[1],
            short_name=row[2],
            from_stop_name=from_stop_name,
            to_stop_name=to_stop_name,
            from_city=from_city,
            to_city=to_city,
            description=row[4],
            type=row[5],
            color=row[6]
        ))
    return routes


async def _store_db_data(session):
    logger.debug('Loading stops to database...')
    fp = GTFS_FP / 'stops.txt'
    if not fp.exists():
        raise GtfsFileNotFound('File stops.txt not found!')

    with open(fp, 'r', encoding='utf-8') as file:
        stops = _process_stops_file(file)
        await db_updater.update_stops(stops, session)
        # await stops_repository.save_stops(stops_to_save)
    logger.debug('Done.')


def _load_memory_data():
    logger.debug('Loading routes to memory storage...')
    fp = GTFS_FP / 'routes.txt'
    if not fp.exists():
        raise GtfsFileNotFound('File routes.txt not found!')

    with open(fp, 'r', encoding='utf-8') as file:

        routes_repository.save_route(route)
    logger.debug('Done.')


async def init_gtfs_data(force_download: bool = False):
    logger.info(f'Data initialization started {"with" if force_download else "without"} downloading files...')
    if force_download or (not (GTFS_FP / 'routes.txt').exists() or not (GTFS_FP / 'stops.txt').exists()):
        n_retries = 5
        for i in range(n_retries, 0, -1):
            try:
                logger.debug(f'Trying to download data, {i} tries remain...')
                await _download_gtfs_data()
                await _store_db_data()
            except Exception as e:
                logger.exception(e)
                await asyncio.sleep(10)
            else:
                break

    _load_memory_data()

    count = await stops_repository.get_stops_count()
    logger.info(f'There are {count} documents in stops collection.')
    if count == 0:
        await _store_db_data()

    logger.info('Data initialization completed!')


async def test():
    import psycopg
    conn = await psycopg.AsyncConnection.connect('host=localhost port=5432 dbname=gtfs user=postgres password=')
    await _store_db_data(conn)

import sys
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(test())
