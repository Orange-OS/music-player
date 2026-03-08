import vlc


class Player:
    def __init__(self):
        self._instance = vlc.Instance()
        self._player = self._instance.media_player_new()
        self._current_path = None

    def load(self, path: str) -> None:
        self._current_path = path
        media = self._instance.media_new(path)
        self._player.set_media(media)

    def play(self) -> None:
        self._player.play()

    def pause(self) -> None:
        self._player.pause()

    def stop(self) -> None:
        self._player.stop()

    def is_playing(self) -> bool:
        return bool(self._player.is_playing())

    def set_position(self, fraction: float) -> None:
        self._player.set_position(max(0.0, min(1.0, fraction)))

    def get_position(self) -> float:
        return float(self._player.get_position())

    def get_time_seconds(self) -> float:
        ms = self._player.get_time()
        return max(0.0, ms / 1000.0) if ms is not None else 0.0

    def get_length_seconds(self) -> float:
        ms = self._player.get_length()
        return max(0.0, ms / 1000.0) if ms is not None else 0.0

    @property
    def current_path(self):
        return self._current_path
