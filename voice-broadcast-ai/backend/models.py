from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class BroadcastAction(str, Enum):
    SET_PREVIEW_SOURCE = "set_preview_source"
    SET_PROGRAM_SOURCE = "set_program_source"
    START_RECORDING = "start_recording"
    STOP_RECORDING = "stop_recording"
    START_STREAM = "start_stream"
    STOP_STREAM = "stop_stream"
    MUTE_MIC = "mute_mic"
    UNMUTE_MIC = "unmute_mic"
    SHOW_GRAPHIC = "show_graphic"
    HIDE_GRAPHIC = "hide_graphic"
    GET_STATUS = "get_status"


class VoiceCommandRequest(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    user_id: str = "operator-1"
    confirmed: bool = False


class ParsedCommand(BaseModel):
    action: BroadcastAction
    parameters: dict[str, Any] = {}
    requires_confirmation: bool = False
    confidence: float = Field(default=1.0, ge=0, le=1)


class CommandResponse(BaseModel):
    success: bool
    message: str
    command: ParsedCommand | None = None
    state: dict[str, Any] | None = None
    confirmation_required: bool = False
