from psycopg.connection_async import AsyncConnection


async def init_db(conn: AsyncConnection):
    query = '''
        -- Ensure that postgis extension is installed        
        CREATE TABLE IF NOT EXISTS agencies (
            id                     SERIAL CONSTRAINT agency_pk PRIMARY KEY,
            name                   VARCHAR(128) NOT NULL,
            url                    VARCHAR(128),
            timezone               VARCHAR(128),
            lang                   VARCHAR(128),
            phone                  VARCHAR(128)
        );
        
        CREATE TABLE IF NOT EXISTS stops (
            id                     INTEGER CONSTRAINT stop_pk PRIMARY KEY,
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
        
        CREATE INDEX IF NOT EXISTS idx_stops_location ON stops USING gist(location);
        
        CREATE TABLE IF NOT EXISTS routes (
            id                     SERIAL CONSTRAINT route_pk PRIMARY KEY,
            agency_id              INTEGER REFERENCES agencies(id),
            short_name             VARCHAR(128) NOT NULL,
            from_stop_name         VARCHAR(128) NOT NULL,
            to_stop_name           VARCHAR(128) NOT NULL,
            from_city              VARCHAR(128),
            to_city                VARCHAR(128),
            description            VARCHAR(128),
            type                   INTEGER,
            color                  VARCHAR(128)
        );
        
        CREATE TABLE IF NOT EXISTS routes_for_stop (
            stop_code              INTEGER PRIMARY KEY,
            route_ids              INTEGER[]
          );
    '''

    await conn.execute(query)
    await conn.commit()
