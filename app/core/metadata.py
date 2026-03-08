from pathlib import Path
from mutagen import File as MutagenFile


def read_metadata(path: Path) -> dict:
    audio = MutagenFile(path, easy=True)
    title = None
    artist = None
    album = None
    duration = None

    if audio is not None:
        title = _first(audio.get("title"))
        artist = _first(audio.get("artist"))
        album = _first(audio.get("album"))
        if audio.info is not None:
            duration = int(audio.info.length)

    if not title:
        title = path.stem

    stat = path.stat()
    return {
        "path": str(path),
        "title": title or "",
        "artist": artist or "",
        "album": album or "",
        "duration": duration or 0,
        "mtime": int(stat.st_mtime),
        "filesize": int(stat.st_size),
    }


def _first(value):
    if not value:
        return None
    if isinstance(value, list):
        return value[0]
    return value
