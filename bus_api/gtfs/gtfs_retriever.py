import asyncio
import io
import os
import ftplib
import zipfile
import logging
import tempfile

import aioftp

from bus_api.config import GTFS_URL
from bus_api.misс import scheduler, daily_trigger

logging.basicConfig(level=logging.DEBUG)
GTFS_FP = '../gtfs_data'
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
        if not os.path.exists(GTFS_FP):
            os.mkdir(GTFS_FP)
        zip_file.extractall(GTFS_FP)
    logger.debug('Done.')


scheduler.add_job(save_gtfs_data, trigger=daily_trigger)
