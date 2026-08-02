from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel
from app import models
from app.deps import get_current_user
from app.voice import transcribe, synthesize_speech_sync

router = APIRouter(prefix="/api/voice", tags=["voice"])

class SpeakIn(BaseModel):
    text: str

@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...), user: models.User = Depends(get_current_user)):
    raw = await audio.read()
    text = transcribe(raw, audio.filename or "audio.wav")
    return {"text": text}

@router.post("/speak")
def speak(payload: SpeakIn, user: models.User = Depends(get_current_user)):
    audio_bytes = synthesize_speech_sync(payload.text)
    return Response(content=audio_bytes, media_type="audio/mpeg")
