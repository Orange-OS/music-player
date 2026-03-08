CREATE TABLE IF NOT EXISTS tracks (
  id INTEGER PRIMARY KEY,
  path TEXT UNIQUE,
  title TEXT,
  artist TEXT,
  album TEXT,
  duration INTEGER,
  mtime INTEGER,
  filesize INTEGER
);

CREATE INDEX IF NOT EXISTS idx_tracks_title ON tracks(title COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_tracks_artist ON tracks(artist COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_tracks_album ON tracks(album COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_tracks_path ON tracks(path COLLATE NOCASE);
