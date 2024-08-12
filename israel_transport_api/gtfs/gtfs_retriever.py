import asyncio
import io
import logging
import pathlib
import zipfile

import httpx
from psycopg.connection_async import AsyncConnection

from israel_transport_api.config import env
from israel_transport_api.gtfs.repository import db_loader
from israel_transport_api.gtfs.repository.init_sql import init_db

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
    logger.info(f'Trying to establish ftp connection with {env.GTFS_URL}...')

    filename = 'israel-public-transportation.zip'
    url = f'{env.GTFS_URL}{filename}'
    bio = io.BytesIO()

    logger.info('Downloading zip file...')

    async with httpx.AsyncClient(verify=False) as session:  # Until they will fix the server...
        async with session.stream('GET', url) as resp:
            async for chunk in resp.aiter_bytes():
                bio.write(chunk)

    logger.info('Done.')

    bio.seek(0)
    return bio


async def _download_gtfs_data():
    logger.info('Starting to update gtfs files...')
    gtfs_data_io = await _download_gtfs_data_from_ftp()

    logger.debug(f'Saving files to {GTFS_FP}...')
    with zipfile.ZipFile(gtfs_data_io) as zip_file:
        if not GTFS_FP.exists():
            GTFS_FP.mkdir()

        zip_file.extractall(GTFS_FP)
    logger.info('Done.')


async def _store_db_data(session, force_load: bool = False):
    await init_db(session)
    await db_loader.load_agencies(session, force_load)
    await db_loader.load_stops(session, force_load)
    await db_loader.load_routes(session, force_load)
    await db_loader.load_routes_for_stop(session, force_load)


async def init_gtfs_data(conn: AsyncConnection, force_download: bool = False):
    logger.info(f'Data initialization started {"with" if force_download else "without"} downloading files...')
    if force_download or (not (GTFS_FP / 'routes.txt').exists() or not (GTFS_FP / 'stops.txt').exists()):
        n_retries = 5
        for i in range(n_retries, 0, -1):
            try:
                logger.info(f'Trying to download data, {i} tries remain...')
                await _download_gtfs_data()
                await _store_db_data(conn)
            except Exception as e:
                logger.exception(e)
                await asyncio.sleep(10)
            else:
                break

    await _store_db_data(conn, force_download)

    logger.info('Data initialization completed!')
