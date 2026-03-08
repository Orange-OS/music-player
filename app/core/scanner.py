from pathlib import Path
from typing import Iterable

AUDIO_EXTS = {".mp3", ".wav", ".flac"}


def scan_folder(folder: Path) -> Iterable[Path]:
    for path in folder.rglob("*"):
        if path.is_file() and path.suffix.lower() in AUDIO_EXTS:
            yield path
