import re
from models import BroadcastAction, ParsedCommand


SOURCE_ALIASES = {
    "camera 1": "camera_1",
    "camera one": "camera_1",
    "कैमरा 1": "camera_1",
    "camera 2": "camera_2",
    "camera two": "camera_2",
    "कैमरा 2": "camera_2",
    "camera 3": "camera_3",
    "camera three": "camera_3",
    "कैमरा 3": "camera_3",
    "reporter": "reporter_1",
    "satellite": "satellite_1",
    "backup": "backup_feed",
    "media player": "media_player_1",
}

MIC_ALIASES = {
    "mic 1": "mic_1",
    "microphone 1": "mic_1",
    "mic 2": "mic_2",
    "microphone 2": "mic_2",
    "mic 3": "mic_3",
    "microphone 3": "mic_3",
    "anchor mic": "anchor_mic",
    "reporter mic": "reporter_mic",
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def find_alias(text: str, aliases: dict[str, str]) -> str | None:
    for phrase in sorted(aliases.keys(), key=len, reverse=True):
        if phrase in text:
            return aliases[phrase]
    return None


def parse_voice_command(raw_text: str) -> ParsedCommand:
    text = normalize_text(raw_text)
    source = find_alias(text, SOURCE_ALIASES)
    microphone = find_alias(text, MIC_ALIASES)

    if any(p in text for p in [
        "status batao", "current status", "broadcast status",
        "system status", "kya live hai"
    ]):
        return ParsedCommand(action=BroadcastAction.GET_STATUS, confidence=0.98)

    if source and any(p in text for p in [
        "preview", "preview par", "preview me", "preview mein"
    ]):
        return ParsedCommand(
            action=BroadcastAction.SET_PREVIEW_SOURCE,
            parameters={"source": source},
            confidence=0.96,
        )

    if source and any(p in text for p in [
        "live karo", "program par", "program me",
        "program mein", "take karo", "take camera"
    ]):
        return ParsedCommand(
            action=BroadcastAction.SET_PROGRAM_SOURCE,
            parameters={"source": source},
            requires_confirmation=True,
            confidence=0.95,
        )

    if any(p in text for p in [
        "recording start", "record start", "record karna start"
    ]):
        return ParsedCommand(
            action=BroadcastAction.START_RECORDING,
            confidence=0.98
        )

    if any(p in text for p in [
        "recording stop", "record stop", "recording band"
    ]):
        return ParsedCommand(
            action=BroadcastAction.STOP_RECORDING,
            requires_confirmation=True,
            confidence=0.98
        )

    if any(p in text for p in [
        "stream start", "streaming start", "go live", "broadcast start"
    ]):
        return ParsedCommand(
            action=BroadcastAction.START_STREAM,
            requires_confirmation=True,
            confidence=0.98
        )

    if any(p in text for p in [
        "stream stop", "streaming stop", "broadcast stop", "live band"
    ]):
        return ParsedCommand(
            action=BroadcastAction.STOP_STREAM,
            requires_confirmation=True,
            confidence=0.98
        )

    if microphone and any(p in text for p in [
        "mute", "band karo", "audio off"
    ]):
        return ParsedCommand(
            action=BroadcastAction.MUTE_MIC,
            parameters={"microphone": microphone},
            confidence=0.95
        )

    if microphone and any(p in text for p in [
        "unmute", "audio on", "mic chalu"
    ]):
        return ParsedCommand(
            action=BroadcastAction.UNMUTE_MIC,
            parameters={"microphone": microphone},
            confidence=0.95
        )

    if any(p in text for p in [
        "breaking news graphic", "breaking graphic"
    ]):
        if any(p in text for p in ["hide", "remove", "hatao", "band"]):
            return ParsedCommand(
                action=BroadcastAction.HIDE_GRAPHIC,
                parameters={"graphic": "breaking_news"},
                confidence=0.95
            )

        return ParsedCommand(
            action=BroadcastAction.SHOW_GRAPHIC,
            parameters={"graphic": "breaking_news"},
            confidence=0.95
        )

    raise ValueError(
        "Command samajh nahi aaya. Example: Camera 2 preview par lagao."
    )
