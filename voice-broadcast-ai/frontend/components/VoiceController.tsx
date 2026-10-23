"use client";

import { useEffect, useRef, useState } from "react";

type BroadcastState = {
  program_source: string;
  preview_source: string;
  recording: boolean;
  streaming: boolean;
  on_air: boolean;
  muted_microphones: string[];
  active_graphic: string | null;
};

type PendingCommand = { text: string };

type SpeechRecognitionEventLike = Event & {
  results: {
    [index: number]: {
      [index: number]: {
        transcript: string;
      };
    };
  };
};

type RecognitionInstance = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onend: (() => void) | null;
  onerror: ((event: Event) => void) | null;
};

declare global {
  interface Window {
    SpeechRecognition?: new () => RecognitionInstance;
    webkitSpeechRecognition?: new () => RecognitionInstance;
  }
}

const API_URL = "http://localhost:8000";
const WS_URL = "ws://localhost:8000/ws";

export default function VoiceController() {
  const recognitionRef = useRef<RecognitionInstance | null>(null);
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [assistantMessage, setAssistantMessage] = useState("Voice controller ready.");
  const [pendingCommand, setPendingCommand] = useState<PendingCommand | null>(null);
  const [broadcastState, setBroadcastState] = useState<BroadcastState | null>(null);

  useEffect(() => {
    const socket = new WebSocket(WS_URL);

    socket.onopen = () => socket.send("dashboard-connected");

    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.state) setBroadcastState(payload.state);
      if (payload.message) setAssistantMessage(payload.message);
    };

    return () => socket.close();
  }, []);

  useEffect(() => {
    const RecognitionConstructor =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!RecognitionConstructor) {
      setAssistantMessage("Speech recognition is not supported in this browser.");
      return;
    }

    const recognition = new RecognitionConstructor();
    recognition.lang = "hi-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const spokenText = event.results[0][0].transcript.trim();
      setTranscript(spokenText);
      void handleSpokenText(spokenText);
    };

    recognition.onend = () => setListening(false);

    recognition.onerror = () => {
      setListening(false);
      setAssistantMessage("Voice recognition error. Please try again.");
    };

    recognitionRef.current = recognition;
  }, [pendingCommand]);

  function speak(text: string) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "hi-IN";
    utterance.rate = 0.95;
    window.speechSynthesis.speak(utterance);
  }

  async function sendCommand(text: string, confirmed = false) {
    const response = await fetch(`${API_URL}/api/voice-command`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        confirmed,
        user_id: "operator-1",
      }),
    });

    const payload = await response.json();

    if (!response.ok) {
      const errorMessage = payload.detail || "Command failed.";
      setAssistantMessage(errorMessage);
      speak(errorMessage);
      return;
    }

    setAssistantMessage(payload.message);
    if (payload.state) setBroadcastState(payload.state);

    if (payload.confirmation_required) {
      setPendingCommand({ text });
    } else {
      setPendingCommand(null);
    }

    speak(payload.message);
  }

  async function handleSpokenText(text: string) {
    const normalized = text.toLowerCase().trim();

    if (
      pendingCommand &&
      ["confirm", "haan confirm", "yes confirm", "kar do", "execute"].some(
        (phrase) => normalized.includes(phrase)
      )
    ) {
      await sendCommand(pendingCommand.text, true);
      return;
    }

    if (
      ["cancel", "cancel karo", "nahi", "mat karo"].some(
        (phrase) => normalized.includes(phrase)
      )
    ) {
      setPendingCommand(null);
      setAssistantMessage("Command cancelled.");
      speak("Command cancelled.");
      return;
    }

    await sendCommand(text);
  }

  function startListening() {
    if (!recognitionRef.current || listening) return;
    setListening(true);
    setTranscript("");
    setAssistantMessage("Listening...");
    recognitionRef.current.start();
  }

  const cardStyle: React.CSSProperties = {
    background: "#171717",
    border: "1px solid #2a2a2a",
    borderRadius: 14,
    padding: 20,
  };

  return (
    <main style={{ minHeight: "100vh", padding: 32, background: "#0a0a0a" }}>
      <section style={{ maxWidth: 1000, margin: "0 auto", display: "grid", gap: 20 }}>
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 34 }}>AI Broadcast Controller</h1>
            <p style={{ color: "#aaa" }}>Voice-controlled production dashboard</p>
          </div>
          <div
            style={{
              padding: "10px 16px",
              borderRadius: 999,
              background: broadcastState?.on_air ? "#dc2626" : "#262626",
              fontWeight: 700,
            }}
          >
            {broadcastState?.on_air ? "● ON AIR" : "OFF AIR"}
          </div>
        </header>

        <section style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div style={cardStyle}>
            <div style={{ color: "#999" }}>PROGRAM</div>
            <div style={{ fontSize: 28, marginTop: 10 }}>
              {broadcastState?.program_source || "Loading"}
            </div>
          </div>
          <div style={cardStyle}>
            <div style={{ color: "#999" }}>PREVIEW</div>
            <div style={{ fontSize: 28, marginTop: 10 }}>
              {broadcastState?.preview_source || "Loading"}
            </div>
          </div>
        </section>

        <section style={cardStyle}>
          <button
            type="button"
            onClick={startListening}
            disabled={listening}
            style={{
              background: "#2563eb",
              color: "white",
              border: 0,
              borderRadius: 10,
              padding: "14px 20px",
              fontWeight: 700,
              opacity: listening ? 0.6 : 1,
            }}
          >
            {listening ? "Listening..." : "🎙 Start Voice Command"}
          </button>

          <div style={{ marginTop: 24 }}>
            <div style={{ color: "#888", fontSize: 12 }}>YOU SAID</div>
            <div style={{ fontSize: 20, marginTop: 6 }}>
              {transcript || "No command yet"}
            </div>
          </div>

          <div style={{ marginTop: 20 }}>
            <div style={{ color: "#888", fontSize: 12 }}>AI RESPONSE</div>
            <div style={{ fontSize: 20, marginTop: 6 }}>{assistantMessage}</div>
          </div>
        </section>

        <section style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
          <StatusCard
            label="Recording"
            value={broadcastState?.recording ? "Active" : "Stopped"}
          />
          <StatusCard
            label="Streaming"
            value={broadcastState?.streaming ? "Live" : "Offline"}
          />
          <StatusCard
            label="Graphic"
            value={broadcastState?.active_graphic || "None"}
          />
        </section>

        {pendingCommand && (
          <section
            style={{
              ...cardStyle,
              borderColor: "#a16207",
              background: "#3b2f10",
            }}
          >
            <strong style={{ color: "#facc15" }}>Confirmation required</strong>
            <p>Say “Confirm” to execute or “Cancel” to stop.</p>
          </section>
        )}
      </section>
    </main>
  );
}

function StatusCard({ label, value }: { label: string; value: string }) {
  return (
    <div
      style={{
        background: "#171717",
        border: "1px solid #2a2a2a",
        borderRadius: 14,
        padding: 20,
      }}
    >
      <div style={{ color: "#999" }}>{label}</div>
      <div style={{ fontSize: 24, marginTop: 10 }}>{value}</div>
    </div>
  );
}
