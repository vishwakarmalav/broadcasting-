# AI Voice Broadcast Controller

This is a starter project for a voice-controlled broadcasting dashboard.

## Features

- Hindi/English voice commands
- Program and preview source switching
- Start/stop recording
- Start/stop stream
- Microphone mute/unmute
- Breaking news graphic control
- Confirmation for critical commands
- Live dashboard state using WebSocket
- Voice response using browser speech synthesis

## Requirements

- Python 3.10+
- Node.js 18+
- Google Chrome recommended

## Run Backend

```bash
cd backend
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install and run:

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Run Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Then open:

```text
http://localhost:3000
```

## Example Voice Commands

```text
Camera 2 preview par lagao
Camera 2 live karo
Recording start karo
Recording stop karo
Stream start karo
Stream stop karo
Mic 1 mute karo
Mic 1 unmute karo
Breaking news graphic dikhao
Breaking news graphic hatao
Current status batao
```

## Important

This starter version controls a simulated broadcast state.

To control real systems, connect `command_router.py` to:
- OBS WebSocket
- vMix API
- ATEM SDK
- FFmpeg
- GStreamer
- NDI
- SRT
- RTMP
