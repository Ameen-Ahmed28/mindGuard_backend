"""
Voice analysis router.
Handles audio upload and emotion detection.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse

from app.schemas.voice import VoiceAnalysisResponse
from app.services.voice_service import voice_service

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["voice"])

# Maximum audio file size (10MB)
MAX_AUDIO_SIZE = 10 * 1024 * 1024


@router.post(
    "/analyze-audio",
    response_model=VoiceAnalysisResponse,
    summary="Analyze voice emotion",
    description="Upload an audio file for emotion detection analysis"
)
async def analyze_audio(
    audio: UploadFile = File(..., description="Audio file (webm, wav, mp3, ogg)")
) -> VoiceAnalysisResponse:
    """
    Analyze emotion from uploaded audio file.
    
    The audio is processed using HuggingFace's emotion classification model
    (prithivMLmods/Speech-Emotion-Classification) and the detected emotion
    with confidence score is returned.
    
    Note: Raw audio is NOT stored. Only the emotion label and confidence
    are returned and can be stored separately.
    
    Args:
        audio: Uploaded audio file
        
    Returns:
        Detected emotion and confidence score
        
    Raises:
        HTTPException: If audio processing fails
    """
    try:
        # Validate file type
        allowed_types = ["audio/webm", "audio/wav", "audio/mp3", "audio/mpeg", "audio/ogg"]
        content_type_base = audio.content_type.split(";")[0] if audio.content_type else ""
        
        if content_type_base not in allowed_types and audio.content_type not in allowed_types:
            # Try to determine from extension
            filename = audio.filename or ""
            extension = filename.split(".")[-1].lower() if "." in filename else ""
            
            if extension not in ["webm", "wav", "mp3", "ogg"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported audio format. Supported formats: webm, wav, mp3, ogg"
                )
            audio_format = extension
        else:
            # Extract format from content type (handle both "audio/webm" and "audio/webm;codecs=opus")
            audio_format = content_type_base.split("/")[-1] if content_type_base else "webm"
            if audio_format == "mpeg":
                audio_format = "mp3"
        
        logger.info(f"Processing audio file: {audio.filename}, type: {audio_format}")
        
        # Read audio data
        audio_data = await audio.read()
        
        if len(audio_data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty audio file"
            )
        
        # Validate file size
        if len(audio_data) > MAX_AUDIO_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Audio file too large. Maximum size is {MAX_AUDIO_SIZE // (1024 * 1024)}MB."
            )
        
        # Analyze emotion
        result = await voice_service.analyze_emotion(audio_data, audio_format)
        
        # Check if voice service returned an error (model not loaded)
        if "error" in result:
            logger.warning(f"Voice analysis unavailable: {result.get('error')}")
            # Return a 503 Service Unavailable with helpful message
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Voice emotion detection is currently unavailable. The PHQ-9 assessment is still available."
            )
        
        logger.info(f"Emotion detected: {result['emotion']} (confidence: {result['confidence']})")
        
        return VoiceAnalysisResponse(
            emotion=result["emotion"],
            confidence=result["confidence"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing audio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze audio. Please try with a different file."
        )
