from pathlib import Path
import base64
from mutagen import File as MutagenFile
from mutagen.flac import Picture


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


def read_embedded_cover(path: Path) -> bytes | None:
    try:
        audio = MutagenFile(path, easy=False)
    except Exception:
        return None

    if audio is None:
        return None

    try:
        if audio.tags is not None:
            if hasattr(audio.tags, "getall"):
                apic_frames = audio.tags.getall("APIC")
                if apic_frames:
                    return apic_frames[0].data
            if "APIC:" in audio.tags:
                apic = audio.tags.get("APIC:")
                if apic is not None:
                    return apic.data

        pictures = getattr(audio, "pictures", None)
        if pictures:
            return pictures[0].data

        covr = None
        if audio.tags is not None and "covr" in audio.tags:
            covr = audio.tags.get("covr")
        if covr:
            item = covr[0] if isinstance(covr, list) else covr
            if item is not None:
                return bytes(item)

        block_picture = None
        if audio.tags is not None and "metadata_block_picture" in audio.tags:
            block_picture = audio.tags.get("metadata_block_picture")
        if block_picture:
            item = block_picture[0] if isinstance(block_picture, list) else block_picture
            if isinstance(item, (bytes, bytearray)):
                data = bytes(item)
                try:
                    pic = Picture(base64.b64decode(data))
                    return pic.data
                except Exception:
                    return data
    except Exception:
        return None

    return None
