import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def _resolve_schema_path() -> Path:
    try:
        import sys

        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        return base / "app" / "data" / "schema.sql"
    except Exception:
        return SCHEMA_PATH


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    schema_path = _resolve_schema_path()
    with schema_path.open("r", encoding="utf-8") as f:
        conn.executescript(f.read())


def upsert_track(conn: sqlite3.Connection, track: dict) -> None:
    conn.execute(
        """
        INSERT INTO tracks(path, title, artist, album, duration, mtime, filesize)
        VALUES(?,?,?,?,?,?,?)
        ON CONFLICT(path) DO UPDATE SET
            title=excluded.title,
            artist=excluded.artist,
            album=excluded.album,
            duration=excluded.duration,
            mtime=excluded.mtime,
            filesize=excluded.filesize
        """,
        (
            track["path"],
            track["title"],
            track["artist"],
            track["album"],
            track["duration"],
            track["mtime"],
            track["filesize"],
        ),
    )


def search_tracks(conn: sqlite3.Connection, query: str) -> list[sqlite3.Row]:
    like = f"%{query}%"
    return conn.execute(
        """
        SELECT * FROM tracks
        WHERE title LIKE ? OR artist LIKE ? OR album LIKE ? OR path LIKE ?
        ORDER BY artist, album, title
        """,
        (like, like, like, like),
    ).fetchall()


def list_tracks(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT * FROM tracks
        ORDER BY artist, album, title
        """
    ).fetchall()
