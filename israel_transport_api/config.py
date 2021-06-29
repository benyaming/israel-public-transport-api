import os


SIRI_URL = os.getenv('SIRI_URL')
GTFS_URL = os.getenv("GTFS_FTP_URL")
API_KEY = os.getenv('API_KEY')

ROOT_PATH = os.getenv("ROOT_PATH")

DB_DSN = f'dbname={os.getenv("DB_NAME", "israel_transport_api")} ' \
               f'user={os.getenv("DB_USER"), "bus_api_admin"} ' \
               f'password={os.getenv("DB_PASS"), ""} ' \
               f'host={os.getenv("DB_HOST"), "localhost"} ' \
               f'port={os.getenv("DB_PORT"), "5432"}'
