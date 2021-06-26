import csv
import io
import zipfile
import logging
import pathlib
from typing import Dict, Tuple

import aioftp

from israel_transport_api.config import GTFS_URL
from israel_transport_api.gtfs.exceptions import GtfsFileNotFound
from israel_transport_api.gtfs.models import Route

logging.basicConfig(level=logging.DEBUG)
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
ROUTES: Dict[Tuple[int, int], Route] = {}


async def download_gtfs_data() -> io.BytesIO:
    logger.debug(f'Trying to establish ftp connection with {GTFS_URL}...')

    async with aioftp.Client.context(GTFS_URL, ) as ftp:
        bio = io.BytesIO()

        logger.debug('Downloading zip file...')
        async with ftp.get_stream('RETR israel-public-transportation.zip') as stream:
            bio.write(await stream.read())

        logger.debug('Done.')
        return bio


async def save_gtfs_data():
    logger.info('Starting to update gtfs files...')
    gtfs_data_io = await download_gtfs_data()

    logger.debug(f'Saving files to {GTFS_FP}...')
    with zipfile.ZipFile(gtfs_data_io) as zip_file:
        if not GTFS_FP.exists():
            GTFS_FP.mkdir()

        zip_file.extractall(GTFS_FP)
    logger.debug('Done.')


async def _store_db_data():
    ...


def _store_memory_data():
    fp = GTFS_FP / 'routes.txt'
    if not fp.exists():
        raise GtfsFileNotFound('File routes.txt not found!')

    with open(fp, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        ...


async def load_gtfs_data():
    if not (GTFS_FP / 'routes.txt').exists():
        await save_gtfs_data()
# scheduler.add_job(save_gtfs_data, trigger=daily_trigger)

_store_memory_data()

