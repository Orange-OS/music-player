from pathlib import Path
import re

_TIME_RE = re.compile(r"\[(\d+):(\d+)(?:\.(\d+))?\]")


def load_lrc_for_track(track_path: str) -> list[tuple[float, str]]:
    path = Path(track_path)
    lrc_path = path.with_suffix(".lrc")
    if not lrc_path.exists():
        return []
    lines = []
    with lrc_path.open("r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            times = _TIME_RE.findall(raw)
            if not times:
                continue
            text = _TIME_RE.sub("", raw).strip()
            for mm, ss, xx in times:
                t = int(mm) * 60 + int(ss)
                if xx:
                    t += int(xx.ljust(2, "0")) / 100
                lines.append((t, text))
    lines.sort(key=lambda x: x[0])
    return lines


def get_line_at_time(lines: list[tuple[float, str]], t: float) -> str:
    current = ""
    for ts, text in lines:
        if t >= ts:
            current = text
        else:
            break
    return current
