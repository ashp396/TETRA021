"""Voice agent plumbing for PennyPal.

Speech to text runs locally with faster whisper, free, no API key.
Text to speech defaults to edge tts, also free and keyless. If you add an
ELEVENLABS_API_KEY, that is used instead for a higher quality PennyPal voice.
"""
import io
import tempfile
import asyncio
import edge_tts
from app.config import settings

_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    return _whisper_model

def transcribe(audio_bytes: bytes, filename_hint: str = "audio.wav") -> str:
    model = get_whisper_model()
    with tempfile.NamedTemporaryFile(suffix="_" + filename_hint, delete=True) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        segments, _ = model.transcribe(tmp.name, language="en")
        return " ".join(seg.text.strip() for seg in segments).strip()

async def _edge_tts(text: str) -> bytes:
    voice = "en-IN-NeerjaNeural"
    communicator = edge_tts.Communicate(text, voice)
    buf = io.BytesIO()
    async for chunk in communicator.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])
    return buf.getvalue()

async def _elevenlabs_tts(text: str) -> bytes:
    import httpx
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.elevenlabs_voice_id}"
    headers = {"xi-api-key": settings.elevenlabs_api_key, "Content-Type": "application/json"}
    payload = {"text": text, "model_id": "eleven_multilingual_v2"}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.content

async def synthesize_speech(text: str) -> bytes:
    if settings.elevenlabs_api_key and settings.elevenlabs_voice_id:
        return await _elevenlabs_tts(text)
    return await _edge_tts(text)

def synthesize_speech_sync(text: str) -> bytes:
    return asyncio.run(synthesize_speech(text))
