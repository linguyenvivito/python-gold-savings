import os
from typing import Any

import httpx
from fastapi import APIRouter
from fastapi import File
from fastapi import Form
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import status

router = APIRouter(prefix="/ai", tags=["ai"])

OPENAI_TRANSCRIPTION_URL = "https://api.openai.com/v1/audio/transcriptions"
DEFAULT_TRANSCRIBE_MODEL = "gpt-4o-transcribe"
MAX_AUDIO_BYTES = int(os.getenv("OPENAI_TRANSCRIBE_MAX_BYTES", "26214400"))


@router.post("/transcribe", status_code=status.HTTP_200_OK)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str | None = Form(default=None),
) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI transcription is not configured on the server.",
        )

    file_bytes = await file.read(MAX_AUDIO_BYTES + 1)
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is required.",
        )

    if len(file_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio file too large. Max {MAX_AUDIO_BYTES} bytes.",
        )

    form_data: dict[str, str] = {
        "model": DEFAULT_TRANSCRIBE_MODEL,
        "response_format": "json",
    }
    if language and language.strip():
        form_data["language"] = language.strip()

    filename = file.filename or "recording.m4a"
    mime_type = (file.content_type or "application/octet-stream").strip()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                OPENAI_TRANSCRIPTION_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                data=form_data,
                files={"file": (filename, file_bytes, mime_type)},
            )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to reach OpenAI transcription service.",
        ) from exc

    if response.status_code >= 400:
        detail = "OpenAI transcription request failed."
        try:
            payload = response.json()
            detail = payload.get("error", {}).get("message") or detail
        except ValueError:
            if response.text:
                detail = response.text

        raise HTTPException(status_code=response.status_code, detail=detail)

    payload = response.json()
    text = str(payload.get("text") or "").strip()

    return {
        "text": text,
        "model": DEFAULT_TRANSCRIBE_MODEL,
    }
