from models import BroadcastAction, ParsedCommand
from broadcast_state import broadcast_state


class BroadcastCommandError(Exception):
    pass


def validate_source(source: str) -> None:
    if source not in broadcast_state.available_sources:
        raise BroadcastCommandError(f"Unknown source: {source}")


def validate_microphone(microphone: str) -> None:
    if microphone not in broadcast_state.available_microphones:
        raise BroadcastCommandError(f"Unknown microphone: {microphone}")


async def execute_command(command: ParsedCommand) -> str:
    action = command.action
    params = command.parameters

    if action == BroadcastAction.GET_STATUS:
        return (
            f"Program source {broadcast_state.program_source} hai. "
            f"Preview source {broadcast_state.preview_source} hai. "
            f"Recording {'on' if broadcast_state.recording else 'off'} hai. "
            f"Streaming {'on' if broadcast_state.streaming else 'off'} hai."
        )

    if action == BroadcastAction.SET_PREVIEW_SOURCE:
        source = params["source"]
        validate_source(source)
        broadcast_state.preview_source = source
        return f"{source} preview par set kar diya gaya hai."

    if action == BroadcastAction.SET_PROGRAM_SOURCE:
        source = params["source"]
        validate_source(source)
        broadcast_state.program_source = source
        broadcast_state.on_air = True
        return f"{source} ab program output par live hai."

    if action == BroadcastAction.START_RECORDING:
        if broadcast_state.recording:
            return "Recording pehle se chal rahi hai."
        broadcast_state.recording = True
        return "Recording start kar di gayi hai."

    if action == BroadcastAction.STOP_RECORDING:
        if not broadcast_state.recording:
            return "Recording already stopped hai."
        broadcast_state.recording = False
        return "Recording stop kar di gayi hai."

    if action == BroadcastAction.START_STREAM:
        if broadcast_state.streaming:
            return "Streaming pehle se live hai."
        broadcast_state.streaming = True
        broadcast_state.on_air = True
        return "Live stream start kar di gayi hai."

    if action == BroadcastAction.STOP_STREAM:
        if not broadcast_state.streaming:
            return "Streaming already stopped hai."
        broadcast_state.streaming = False
        broadcast_state.on_air = False
        return "Live stream stop kar di gayi hai."

    if action == BroadcastAction.MUTE_MIC:
        microphone = params["microphone"]
        validate_microphone(microphone)
        broadcast_state.muted_microphones.add(microphone)
        return f"{microphone} mute kar diya gaya hai."

    if action == BroadcastAction.UNMUTE_MIC:
        microphone = params["microphone"]
        validate_microphone(microphone)
        broadcast_state.muted_microphones.discard(microphone)
        return f"{microphone} unmute kar diya gaya hai."

    if action == BroadcastAction.SHOW_GRAPHIC:
        graphic = params.get("graphic", "breaking_news")
        broadcast_state.active_graphic = graphic
        return f"{graphic} graphic screen par dikha diya gaya hai."

    if action == BroadcastAction.HIDE_GRAPHIC:
        broadcast_state.active_graphic = None
        return "Active graphic hata diya gaya hai."

    raise BroadcastCommandError(f"Unsupported action: {action}")
