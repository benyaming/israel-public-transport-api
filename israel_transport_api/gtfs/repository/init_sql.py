from psycopg.connection_async import AsyncConnection


async def init_db(conn: AsyncConnection):
    query = '''
        CREATE EXTENSION IF NOT EXISTS postgis;
        
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
        
        CREATE TABLE IF NOT EXISTS trips (
            id                     BIGSERIAL CONSTRAINT trip_pk PRIMARY KEY,
            route_id               INTEGER REFERENCES routes(id),
            service_id             INTEGER,
            headsign               VARCHAR(128),
            direction_id           INTEGER
        );
        
        CREATE TABLE IF NOT EXISTS stop_times (
            trip_id BIGINT NOT NULL REFERENCES trips(id),
            stop_id INT NOT NULL REFERENCES stops(id),
            stop_sequence INTEGER NOT NULL,
            PRIMARY KEY (trip_id, stop_id, stop_sequence)
        );
        
        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_stop_times_trip_id ON stop_times (trip_id);
        CREATE INDEX IF NOT EXISTS idx_stop_times_stop_id ON stop_times (stop_id);
    '''

    await conn.execute(query)
    await conn.commit()
