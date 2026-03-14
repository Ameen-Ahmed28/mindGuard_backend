"""
Voice Service for emotion detection using HuggingFace transformers.
Uses the prithivMLmods/Speech-Emotion-Classification model.

Preprocessing requirements for Wav2Vec2-based models:
- Sampling rate: 16kHz
- Normalization: True (zero mean, unit variance)
- Mono channel
"""

import os
# Fix LLVM SVML error on Windows - must be set before importing torch
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
# Disable Intel MKL SVML optimizations that cause issues on some Windows systems
os.environ['MKL_DEBUG_CPU_TYPE'] = '5'  # Force generic CPU path

import io
import logging
import tempfile
import threading
import numpy as np
from typing import Optional

from transformers import (
    Wav2Vec2ForSequenceClassification,
    Wav2Vec2FeatureExtractor,
    pipeline
)
import librosa
import soundfile as sf
import torch

from app.config import settings

# Model label mapping (3-letter codes to full emotion names)
# Model outputs: ANG, CAL, DIS, FEA, HAP, NEU, SAD, SUR
EMOTION_LABEL_MAP = {
    "ang": "Anger",
    "cal": "Calm",
    "dis": "Disgust",
    "fea": "Fear",
    "hap": "Happiness",
    "neu": "Neutral",
    "sad": "Sadness",
    "sur": "Surprise"
}

SUPPORTED_EMOTIONS = list(EMOTION_LABEL_MAP.values())

# Configure logging
logger = logging.getLogger(__name__)


class VoiceService:
    """Service for voice emotion detection using HuggingFace models."""
    
    _instance = None
    _model = None
    _feature_extractor = None
    _lock = threading.Lock()
    _initialized = False
    _load_error = None  # Track if model loading failed
    
    def __new__(cls):
        """Singleton pattern to avoid loading model multiple times."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the voice service - model is loaded lazily on first use."""
        # Don't load model here - do it lazily
        pass
    
    def _ensure_model_loaded(self) -> bool:
        """
        Ensure the model is loaded. Called before any operation that needs the model.
        
        Returns:
            True if model is available, False if loading failed
        """
        with self._lock:
            if self._model is not None and self._feature_extractor is not None:
                return True
            
            if self._load_error is not None:
                # Already tried and failed
                logger.warning(f"Voice model previously failed to load: {self._load_error}")
                return False
            
            # Try to load the model
            try:
                logger.info(f"Loading emotion classification model: {settings.emotion_model}")
                
                # Load model and feature extractor separately for proper preprocessing
                self._model = Wav2Vec2ForSequenceClassification.from_pretrained(
                    settings.emotion_model
                )
                self._feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(
                    settings.emotion_model
                )
                
                # Set model to evaluation mode
                self._model.eval()
                
                logger.info("Emotion classification model loaded successfully")
                logger.info(f"Feature extractor config: {self._feature_extractor.to_dict()}")
                return True
                
            except Exception as e:
                self._load_error = str(e)
                logger.error(f"Failed to load emotion classification model: {e}")
                logger.warning("Voice emotion detection will be unavailable. App will continue with limited functionality.")
                return False
    
    def _convert_audio_to_wav(self, audio_data: bytes, original_format: str = "webm") -> str:
        """
        Convert audio data to WAV format suitable for the model.
        
        Args:
            audio_data: Raw audio bytes
            original_format: Original audio format (webm, mp3, etc.)
            
        Returns:
            Path to temporary WAV file
        """
        try:
            # Try using pydub for conversion if available
            from pydub import AudioSegment
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix=f".{original_format}", delete=False) as temp_input:
                temp_input.write(audio_data)
                input_path = temp_input.name
            
            # Convert to WAV
            audio = AudioSegment.from_file(input_path, format=original_format)
            
            # Create output temp file
            output_path = tempfile.mktemp(suffix=".wav")
            audio.export(output_path, format="wav")
            
            # Clean up input file
            os.unlink(input_path)
            
            return output_path
            
        except ImportError:
            # Fallback: try direct loading with librosa
            logger.warning("pydub not available, attempting direct audio loading")
            return None
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            return None
    
    def _load_audio(self, audio_data: bytes, audio_format: str = "webm") -> np.ndarray:
        """
        Load and preprocess audio data for the model.
        
        Steps:
        1. Convert to WAV if needed
        2. Load with librosa at 16kHz
        3. Convert to mono if stereo
        4. Normalize using Wav2Vec2FeatureExtractor
        
        Args:
            audio_data: Raw audio bytes
            audio_format: Audio format (webm, wav, mp3, etc.)
            
        Returns:
            Preprocessed audio array ready for the model
        """
        temp_file = None
        audio_array = None
        
        try:
            # Convert to WAV if not already
            if audio_format.lower() != "wav":
                temp_file = self._convert_audio_to_wav(audio_data, audio_format)
                if temp_file:
                    # Load the converted WAV file
                    audio_array, sr = librosa.load(temp_file, sr=16000, mono=True)
                else:
                    # Try direct loading with librosa
                    audio_array, sr = librosa.load(io.BytesIO(audio_data), sr=16000, mono=True)
            else:
                # Load WAV directly
                audio_array, sr = librosa.load(io.BytesIO(audio_data), sr=16000, mono=True)
            
            # Log audio stats for debugging
            if audio_array is not None:
                logger.info(f"Audio loaded: shape={audio_array.shape}, "
                           f"duration={len(audio_array)/16000:.2f}s, "
                           f"min={audio_array.min():.4f}, max={audio_array.max():.4f}, "
                           f"mean={audio_array.mean():.4f}, std={audio_array.std():.4f}")
            
            return audio_array
            
        finally:
            # Clean up temporary files
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass
    
    async def analyze_emotion(self, audio_data: bytes, audio_format: str = "webm") -> dict:
        """
        Analyze emotion from audio data using proper Wav2Vec2 preprocessing.
        
        Args:
            audio_data: Raw audio bytes
            audio_format: Audio format (webm, wav, mp3, etc.)
            
        Returns:
            Dictionary with 'emotion' and 'confidence' keys
        """
        # Ensure model is loaded (lazy loading)
        if not self._ensure_model_loaded():
            logger.warning("Voice model not available, returning default neutral emotion")
            return {
                "emotion": "neutral",
                "confidence": 0.5,
                "error": "Voice emotion detection unavailable - model not loaded"
            }
        
        try:
            # Load and preprocess audio
            audio_array = self._load_audio(audio_data, audio_format)
            
            if audio_array is None or len(audio_array) < 8000:  # Less than 0.5 seconds
                logger.warning("Audio too short or failed to load")
                return {
                    "emotion": "neutral",
                    "confidence": 0.5
                }
            
            # Use feature extractor for proper preprocessing
            # This normalizes the audio (zero mean, unit variance) as required by Wav2Vec2
            inputs = self._feature_extractor(
                audio_array,
                sampling_rate=16000,
                return_tensors="pt",
                padding=True,
                do_normalize=True  # Critical for Wav2Vec2 models
            )
            
            # Run inference
            with torch.no_grad():
                outputs = self._model(**inputs)
                logits = outputs.logits
                
                # Apply softmax to get probabilities
                probabilities = torch.nn.functional.softmax(logits, dim=-1)
                
                # Get top prediction
                confidence, predicted_class = torch.max(probabilities, dim=-1)
                
                # Get all scores for debugging
                all_scores = probabilities[0].tolist()
                
                # Map class index to label
                id2label = self._model.config.id2label
                raw_label = id2label[predicted_class.item()].lower()
                confidence_value = round(confidence.item(), 4)
                
                # Map 3-letter model labels to full emotion names
                emotion = EMOTION_LABEL_MAP.get(raw_label, raw_label)
                
                # Log all predictions for debugging
                logger.info(f"All class scores: {[(id2label[i], round(s, 4)) for i, s in enumerate(all_scores)]}")
                logger.info(f"Predicted: {raw_label} -> {emotion} (confidence: {confidence_value})")
                
                return {
                    "emotion": emotion,
                    "confidence": confidence_value
                }
                
        except Exception as e:
            logger.error(f"Error analyzing emotion: {e}")
            import traceback
            traceback.print_exc()
            # Return neutral on error
            return {
                "emotion": "neutral",
                "confidence": 0.5
            }
    
    def is_model_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._model is not None and self._feature_extractor is not None
    
    def is_available(self) -> bool:
        """Check if voice emotion detection is available."""
        return self._ensure_model_loaded()


# Create singleton instance (model loaded lazily on first use)
voice_service = VoiceService()
