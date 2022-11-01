async def init_db():
    query = '''
    CREATE EXTENSION IF NOT EXISTS postgis;
    
    CREATE TABLE IF NOT EXISTS stop (
        id                     SERIAL CONSTRAINT stop_pk PRIMARY KEY,
        city                   VARCHAR(128),
        code                   INTEGER NOT NULL,
        floor                  INTEGER,
        location               GEOGRAPHY(POINT),
        location_type          INTEGER,
        name                   VARCHAR(128) NOT NULL,
        parent_station_id      INTEGER,
        platform               INTEGER,
        street                 VARCHAR(128),
        zone_id                INTEGER
    );
    
    CREATE INDEX IF NOT EXISTS idx_stops_location ON stop USING gist(location);
    '''

