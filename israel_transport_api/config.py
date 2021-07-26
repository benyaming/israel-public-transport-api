import os


SIRI_URL = os.getenv('SIRI_URL')
GTFS_URL = os.getenv("GTFS_FTP_URL")
API_KEY = os.getenv('API_KEY')

ROOT_PATH = os.getenv('ROOT_PATH', '')

DB_URL = os.getenv('DB_URL')
DB_NAME = os.getenv('DB_NAME')

SCHED_HOURS = os.getenv('SCHED_HOURS')
SCHED_MINS = os.getenv('SCHED_MINS')
