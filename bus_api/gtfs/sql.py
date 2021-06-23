init_query = '''
CREATE TABLE IF NOT EXISTS agency
(
  agency_id         TEXT UNIQUE NULL,
  agency_name       TEXT NOT NULL,
  agency_url        TEXT NOT NULL,
  agency_timezone   TEXT NOT NULL,
  agency_lang       TEXT NULL,
  agency_phone      TEXT NULL,
  agency_fare_url   TEXT NULL 
);

CREATE TABLE IF NOT EXISTS stops
(
  stop_id           TEXT PRIMARY KEY,
  stop_code         TEXT NULL,
  stop_name         TEXT NOT NULL,
  stop_desc         TEXT NULL,
  stop_lat          double precision NOT NULL,
  stop_lon          double precision NOT NULL,
  zone_id           text NULL
);

CREATE TABLE IF NOT EXISTS routes
(
  route_id          text PRIMARY KEY,
  agency_id         text NULL,
  route_short_name  text NULL,
  route_long_name   text NULL,
  route_type        integer NULL,
  route_url         text NULL,
  route_color       text NULL
);

CREATE TABLE IF NOT EXISTS calendar_dates
(
  service_id text NOT NULL,
  date numeric(8) NOT NULL,
  exception_type integer NOT NULL
);

CREATE TABLE IF NOT EXISTS shapes
(
  shape_id          text,
  shape_pt_lat      double precision NOT NULL,
  shape_pt_lon      double precision NOT NULL,
  shape_pt_sequence integer NOT NULL,
  shape_dist_traveled text NULL
);

CREATE TABLE IF NOT EXISTS trips
(
  route_id          text NOT NULL,
  service_id        text NOT NULL,
  trip_id           text NOT NULL PRIMARY KEY,
  trip_headsign     text NULL,
  direction_id      boolean NULL,
  block_id          text NULL,
  shape_id          text NULL,
  scheduled_trip_id text NULL
);

CREATE TABLE IF NOT EXISTS stop_times
(
  trip_id           text NOT NULL,
  arrival_time      interval NOT NULL,
  departure_time    interval NOT NULL,
  stop_id           text NOT NULL,
  stop_sequence     integer NOT NULL,
  pickup_type       integer NULL CHECK(pickup_type >= 0 and pickup_type <=3),
  drop_off_type     integer NULL CHECK(drop_off_type >= 0 and drop_off_type <=3),
  shape_dist_traveled double precision NULL
);
'''
