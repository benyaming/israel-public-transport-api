from israel_transport_api import misс


async def check_tables():
    init_query = '''
    CREATE TABLE IF NOT EXISTS stops
    (
      id           INT PRIMARY KEY,
      code         INT UNIQUE,
      name         TEXT NOT NULL,
      street       TEXT NULL,
      city         TEXT NOT NULL,
      platform     TEXT NULL,
      floor        TEXT NULL,
      location     POINT NOT NULL,
      zone_id      TEXT NULL
    );
    '''
    async with misс.pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(init_query)


async def save_stops():
    ...


async def find_stop_by_id():
    ...


async def find_stops_in_area(lat: float, lng: float, radius: int):
    ...
