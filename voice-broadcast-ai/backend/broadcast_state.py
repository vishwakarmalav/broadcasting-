from dataclasses import asdict, dataclass, field


@dataclass
class BroadcastState:
    program_source: str = "camera_1"
    preview_source: str = "camera_2"
    recording: bool = False
    streaming: bool = False
    on_air: bool = False
    muted_microphones: set[str] = field(default_factory=set)
    active_graphic: str | None = None

    available_sources: list[str] = field(default_factory=lambda: [
        "camera_1",
        "camera_2",
        "camera_3",
        "reporter_1",
        "satellite_1",
        "media_player_1",
        "backup_feed",
    ])

    available_microphones: list[str] = field(default_factory=lambda: [
        "mic_1",
        "mic_2",
        "mic_3",
        "anchor_mic",
        "reporter_mic",
    ])

    def to_dict(self) -> dict:
        data = asdict(self)
        data["muted_microphones"] = sorted(self.muted_microphones)
        return data


broadcast_state = BroadcastState()
