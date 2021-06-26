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
