import csv
import io
import zipfile
import logging
import pathlib
from typing import Dict, Tuple

import aioftp

from israel_transport_api import misс
from israel_transport_api.config import GTFS_URL
from israel_transport_api.gtfs.exceptions import GtfsFileNotFound
from israel_transport_api.gtfs.models import Route
from israel_transport_api.gtfs.utils import parse_route_long_name

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
    logger.debug(f'Trying to establish ftp connection with {GTFS_URL}...')

    async with aioftp.Client.context(GTFS_URL, ) as ftp:
        bio = io.BytesIO()

        logger.debug('Downloading zip file...')
        async with ftp.get_stream('RETR israel-public-transportation.zip') as stream:
            bio.write(await stream.read())

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


async def _store_db_data():
    logger.debug('Loading stops to database...')
    fp = GTFS_FP / 'stops.txt'
    if not fp.exists():
        raise GtfsFileNotFound('File stops.txt not found!')

    with open(fp, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)

        is_headers_skipped = False
        for row in reader:
            if not is_headers_skipped:
                is_headers_skipped = True
                continue
            # todo


def _load_memory_data():
    logger.debug('Loading routes to memory storage...')
    fp = GTFS_FP / 'routes.txt'
    if not fp.exists():
        raise GtfsFileNotFound('File routes.txt not found!')

    with open(fp, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)

        is_headers_skipped = False
        for row in reader:
            if not is_headers_skipped:
                is_headers_skipped = True
                continue

            from_stop_name, from_city, to_stop_name, to_city = parse_route_long_name(row[3])
            route = Route(
                id=row[0],
                agency_id=row[1],
                short_name=row[2],
                from_stop_name=from_stop_name,
                to_stop_name=to_stop_name,
                from_city=from_city,
                to_city=to_city,
                description=row[4],
                type=row[5],
                color=row[6]
            )
            misс.ROUTES_STORE[row[0]] = route
    logger.debug('Done.')


async def init_gtfs_data(force_download: bool = False):
    if not force_download and (not (GTFS_FP / 'routes.txt').exists() or not (GTFS_FP / 'stops.txt').exists()):
        await _download_gtfs_data()

    _load_memory_data()


# scheduler.add_job(save_gtfs_data, trigger=daily_trigger)
