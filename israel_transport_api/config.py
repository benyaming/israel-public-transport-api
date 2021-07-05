import os


SIRI_URL = os.getenv('SIRI_URL')
GTFS_URL = os.getenv("GTFS_FTP_URL")
API_KEY = os.getenv('API_KEY')

ROOT_PATH = os.getenv('ROOT_PATH', '')

DB_URL = os.getenv('DB_URL')
DB_NAME = os.getenv('DB_NAME')
