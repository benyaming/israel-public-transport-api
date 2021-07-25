import csv
import ftplib
import io
import logging
import pathlib
import zipfile


from israel_transport_api.config import GTFS_URL
from israel_transport_api.gtfs.exceptions import GtfsFileNotFound
from israel_transport_api.gtfs.models import Route
from israel_transport_api.gtfs.repository import stops_repository, routes_repository
from israel_transport_api.gtfs.utils import parse_route_long_name, parse_stop_description

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

    ftp = ftplib.FTP(GTFS_URL)
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


async def _store_db_data():
    logger.debug('Loading stops to database...')
    fp = GTFS_FP / 'stops.txt'
    if not fp.exists():
        raise GtfsFileNotFound('File stops.txt not found!')

    with open(fp, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)  # skip headers

        stops_to_save = []
        for row in reader:
            street, city, platform, floor = parse_stop_description(row[3])
            stops_to_save.append({
                '_id': int(row[0]),
                'code': int(row[1]),
                'name': row[2],
                'street': street,
                'city': city,
                'platform': platform,
                'floor': floor,
                'location': {
                    'type': 'Point',
                    'coordinates': (float(row[4]), float(row[5]))
                },
                'location_type': row[6],
                'parent_station_id': row[7],
                'zone_id': row[8]
            })
        await stops_repository.save_stops(stops_to_save)
    logger.debug('Done.')


def _load_memory_data():
    logger.debug('Loading routes to memory storage...')
    fp = GTFS_FP / 'routes.txt'
    if not fp.exists():
        raise GtfsFileNotFound('File routes.txt not found!')

    with open(fp, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)  # skip headers

        for row in reader:
            from_stop_name, from_city, to_stop_name, to_city = parse_route_long_name(row[3])
            route = Route(
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
            )
            routes_repository.save_route(route)
    logger.debug('Done.')


async def init_gtfs_data(force_download: bool = False):
    logger.info(f'Data initialization started {"with" if force_download else "without"} downloading files...')
    if force_download or (not (GTFS_FP / 'routes.txt').exists() or not (GTFS_FP / 'stops.txt').exists()):
        await _download_gtfs_data()

    _load_memory_data()

    count = await stops_repository.get_stops_count()
    logger.info(f'There are {count} documents in stops collection.')
    if count == 0:
        await _store_db_data()

    logger.info('Data initialization completed!')
