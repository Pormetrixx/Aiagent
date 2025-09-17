"""
Speech-to-Text module using OpenAI Whisper for local speech recognition
"""
import os
import logging
import numpy as np
import torch
import whisper
from typing import Optional, Dict, Any
import soundfile as sf
from pathlib import Path

logger = logging.getLogger(__name__)


class WhisperSTT:
    """Speech-to-Text using OpenAI Whisper"""
    
    def __init__(self, model_size: str = "base", device: str = "auto", language: str = "de"):
        """
        Initialize Whisper STT
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            device: Device to use (cpu, cuda, auto)
            language: Language code for recognition
        """
        self.model_size = model_size
        self.language = language
        
        # Auto-detect device if needed
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model"""
        try:
            logger.info(f"Loading Whisper model '{self.model_size}' on device '{self.device}'")
            self.model = whisper.load_model(self.model_size, device=self.device)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            raise
    
    def transcribe_file(self, audio_file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Transcribe audio file to text
        
        Args:
            audio_file_path: Path to audio file
            **kwargs: Additional Whisper options
            
        Returns:
            Dictionary with transcription results
        """
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        try:
            # Set default options
            options = {
                "language": self.language,
                "fp16": False if self.device == "cpu" else True,
                **kwargs
            }
            
            logger.debug(f"Transcribing audio file: {audio_file_path}")
            result = self.model.transcribe(audio_file_path, **options)
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", self.language),
                "segments": result.get("segments", []),
                "confidence": self._calculate_average_confidence(result.get("segments", []))
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    def transcribe_audio_data(self, audio_data: np.ndarray, sample_rate: int = 16000, **kwargs) -> Dict[str, Any]:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of audio data
            **kwargs: Additional Whisper options
            
        Returns:
            Dictionary with transcription results
        """
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            # Ensure audio is in the right format for Whisper
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Normalize audio if needed
            if np.abs(audio_data).max() > 1.0:
                audio_data = audio_data / np.abs(audio_data).max()
            
            # Set default options
            options = {
                "language": self.language,
                "fp16": False if self.device == "cpu" else True,
                **kwargs
            }
            
            logger.debug("Transcribing audio data")
            result = self.model.transcribe(audio_data, **options)
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", self.language),
                "segments": result.get("segments", []),
                "confidence": self._calculate_average_confidence(result.get("segments", []))
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio data: {e}")
            raise
    
    def _calculate_average_confidence(self, segments: list) -> float:
        """Calculate average confidence from segments"""
        if not segments:
            return 0.0
        
        confidences = []
        for segment in segments:
            if "avg_logprob" in segment:
                # Convert log probability to confidence (rough approximation)
                confidence = np.exp(segment["avg_logprob"])
                confidences.append(confidence)
        
        return np.mean(confidences) if confidences else 0.0
    
    def is_available(self) -> bool:
        """Check if the STT system is available"""
        return self.model is not None


class AudioProcessor:
    """Helper class for audio processing tasks"""
    
    @staticmethod
    def load_audio_file(file_path: str) -> tuple[np.ndarray, int]:
        """
        Load audio file and return audio data and sample rate
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            audio_data, sample_rate = sf.read(file_path)
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            return audio_data, sample_rate
            
        except Exception as e:
            logger.error(f"Error loading audio file {file_path}: {e}")
            raise
    
    @staticmethod
    def save_audio_file(audio_data: np.ndarray, file_path: str, sample_rate: int = 16000):
        """
        Save audio data to file
        
        Args:
            audio_data: Audio data as numpy array
            file_path: Output file path
            sample_rate: Sample rate
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            sf.write(file_path, audio_data, sample_rate)
            logger.debug(f"Audio saved to: {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving audio file {file_path}: {e}")
            raise
    
    @staticmethod
    def normalize_audio(audio_data: np.ndarray) -> np.ndarray:
        """
        Normalize audio data to [-1, 1] range
        
        Args:
            audio_data: Input audio data
            
        Returns:
            Normalized audio data
        """
        max_val = np.abs(audio_data).max()
        if max_val > 0:
            return audio_data / max_val
        return audio_data
    
    @staticmethod
    def resample_audio(audio_data: np.ndarray, original_rate: int, target_rate: int) -> np.ndarray:
        """
        Resample audio to target sample rate
        
        Args:
            audio_data: Input audio data
            original_rate: Original sample rate
            target_rate: Target sample rate
            
        Returns:
            Resampled audio data
        """
        try:
            import librosa
            return librosa.resample(audio_data, orig_sr=original_rate, target_sr=target_rate)
        except ImportError:
            logger.warning("librosa not available for resampling, returning original audio")
            return audio_data
        except Exception as e:
            logger.error(f"Error resampling audio: {e}")
            return audio_data


def create_stt_engine(config: Dict[str, Any]) -> WhisperSTT:
    """
    Factory function to create STT engine based on configuration
    
    Args:
        config: STT configuration dictionary
        
    Returns:
        Configured STT engine
    """
    engine_type = config.get("engine", "whisper").lower()
    
    if engine_type == "whisper":
        return WhisperSTT(
            model_size=config.get("model_size", "base"),
            device=config.get("device", "auto"),
            language=config.get("language", "de")
        )
    else:
        raise ValueError(f"Unsupported STT engine: {engine_type}")