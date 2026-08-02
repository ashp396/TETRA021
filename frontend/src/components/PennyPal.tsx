"use client";
import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";

function PennyIcon({ size = 36 }: { size?: number }) {
  return (
    <svg viewBox="0 0 100 100" style={{ width: size, height: size }}>
      <circle cx="50" cy="50" r="46" fill="#d7a83f" stroke="#f0c667" strokeWidth="3" />
      <circle cx="34" cy="46" r="9" fill="#1a1220" />
      <circle cx="66" cy="46" r="9" fill="#1a1220" />
      <circle cx="37" cy="43" r="3" fill="#fff" />
      <circle cx="69" cy="43" r="3" fill="#fff" />
      <path d="M38 66 Q50 76 62 66" stroke="#1a1220" strokeWidth="4" fill="none" strokeLinecap="round" />
      <path d="M20 30 L30 18 L36 32 Z" fill="#c1447e" />
      <path d="M80 30 L70 18 L64 32 Z" fill="#c1447e" />
    </svg>
  );
} 

export default function PennyPal() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<{ role: string; text: string }[]>([
    { role: "bot", text: "Hi, I am PennyPal. Ask me about anything in your uploaded documents, your score, or a discrepancy." },
  ]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const [listening, setListening] = useState(false);
  const recogRef = useRef<any>(null);
  const bodyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (bodyRef.current) bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
  }, [messages, open]);

  function speakBrowser(text: string) {
    // Falls back to the browser voice for instant playback; the backend
    // /api/voice/speak endpoint (edge tts, or ElevenLabs if configured)
    // can be wired in for a nicer PennyPal voice by fetching that audio
    // and playing it instead of using speechSynthesis.
    try {
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      u.rate = 1.02; u.pitch = 1.1;
      window.speechSynthesis.speak(u);
    } catch (e) {}
  }

  async function playServerVoice(text: string) {
    try {
      const res = await api.post("/api/voice/speak", { text }, { responseType: "blob" });
      const url = URL.createObjectURL(res.data);
      new Audio(url).play();
    } catch (e) {
      speakBrowser(text);
    }
  }

  function startListening() {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SR) {
      setMessages((m) => [...m, { role: "bot", text: "Voice input is not supported in this browser." }]);
      return;
    }
    const recog = new SR();
    recog.lang = "en-IN";
    recog.onresult = (e: any) => setInput(e.results[0][0].transcript);
    recog.onend = () => setListening(false);
    recog.onerror = () => setListening(false);
    recogRef.current = recog;
    recog.start();
    setListening(true);
  }
  function stopListening() {
    recogRef.current?.stop();
    setListening(false);
  }

  async function send(text?: string) {
    const q = (text ?? input).trim();
    if (!q) return;
    setMessages((m) => [...m, { role: "user", text: q }]);
    setInput("");
    setThinking(true);
    try {
      const res = await api.post("/api/chat/message", { message: q });
      const answer = res.data.answer as string;
      setMessages((m) => [...m, { role: "bot", text: answer }]);
      playServerVoice(answer);
    } catch (e) {
      setMessages((m) => [...m, { role: "bot", text: "Sorry, I could not reach the analysis engine just now." }]);
    }
    setThinking(false);
  }

  return (
    <>
      <button
        className="fixed bottom-6 right-6 w-16 h-16 rounded-full flex items-center justify-center shadow-xl z-50"
        style={{ background: "linear-gradient(135deg,#c1447e,#d7a83f)" }}
        onClick={() => setOpen(!open)}
      >
        <PennyIcon size={40} />
      </button>
      {open && (
        <div className="fixed bottom-24 right-6 w-[360px] max-w-[92vw] h-[520px] max-h-[75vh] bg-surface border border-line rounded-2xl z-50 flex flex-col overflow-hidden shadow-2xl uiFont">
          <div className="flex items-center gap-2 p-3 border-b border-line bg-surface2">
            <PennyIcon size={30} />
            <div>
              <div className="text-sm font-bold">PennyPal</div>
              <div className="text-xs text-muted">Your fundraising co pilot</div>
            </div>
            <button className="ml-auto text-muted" onClick={() => setOpen(false)}>✕</button>
          </div>
          <div className="flex-1 overflow-y-auto p-3 text-sm" ref={bodyRef}>
            {messages.map((m, i) => (
              <div
                key={i}
                className="mb-3 max-w-[85%] p-2 px-3 rounded-2xl leading-relaxed"
                style={m.role === "user"
                  ? { background: "linear-gradient(135deg,#c1447e,#e069a0)", color: "#fff", marginLeft: "auto" }
                  : { background: "#2a1f40", border: "1px solid #3a2c54" }}
              >
                {m.text}
              </div>
            ))}
            {thinking && <div className="text-muted text-xs">Thinking…</div>}
          </div>
          <div className="flex gap-2 p-3 border-t border-line">
            <button
              className="w-9 h-9 rounded-lg border border-line"
              style={listening ? { background: "#e0587a", color: "#fff" } : {}}
              onClick={listening ? stopListening : startListening}
            >
              🎤
            </button>
            <input
              className="flex-1 p-2 rounded-lg bg-surface2 border border-line text-sm"
              placeholder="Ask anything about your documents"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") send(); }}
            />
            <button className="w-9 h-9 rounded-lg" style={{ background: "#d7a83f", color: "#1a1220" }} onClick={() => send()}>➤</button>
          </div>
        </div>
      )}
    </>
  );
}
