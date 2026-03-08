from pathlib import Path
from typing import Iterable

from .scanner import scan_folder
from .metadata import read_metadata
from ..data import db


def init_library(conn) -> None:
    db.init_db(conn)


def scan_and_index(conn, folder: Path) -> int:
    count = 0
    for path in scan_folder(folder):
        track = read_metadata(path)
        db.upsert_track(conn, track)
        count += 1
    conn.commit()
    return count


def list_all(conn) -> list:
    return db.list_tracks(conn)


def search(conn, query: str) -> list:
    if not query.strip():
        return list_all(conn)
    return db.search_tracks(conn, query)


def get_track_by_path(conn, path: str):
    return db.get_track_by_path(conn, path)
