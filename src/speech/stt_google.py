"""
Speech-to-Text using Google Cloud Speech-to-Text
"""
import os
import logging
from typing import Dict, Any, Union, Optional
import numpy as np
from pathlib import Path
from .base import BaseSTTEngine

logger = logging.getLogger(__name__)


class GoogleSTT(BaseSTTEngine):
    """Speech-to-Text using Google Cloud Speech-to-Text"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Google Cloud STT
        
        Args:
            config: Configuration dictionary with:
                - credentials_path: Path to Google Cloud credentials JSON
                - language: Language code (default: de-DE)
                - model: Model to use (default: latest_long)
        """
        super().__init__(config)
        self.credentials_path = config.get("credentials_path") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.model = config.get("model", "latest_long")
        self.client = None
        
        # Google uses de-DE format instead of just de
        if self.language == "de":
            self.language = "de-DE"
        
        if not self.credentials_path:
            logger.warning("Google Cloud credentials not provided")
        else:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Cloud Speech client"""
        try:
            from google.cloud import speech
            
            # Set credentials environment variable if not already set
            if self.credentials_path and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path
            
            self.client = speech.SpeechClient()
            self.speech = speech
            
            logger.info("Google Cloud Speech client initialized successfully")
            
        except ImportError:
            logger.error("Google Cloud Speech not installed. Install with: pip install google-cloud-speech")
            self.client = None
        except Exception as e:
            logger.error(f"Error initializing Google Cloud Speech client: {e}")
            self.client = None
    
    def transcribe_file(self, audio_file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Transcribe audio file to text using Google Cloud
        
        Args:
            audio_file_path: Path to audio file
            **kwargs: Additional Google Cloud options
            
        Returns:
            Dictionary with transcription results
        """
        if not self.client:
            raise RuntimeError("Google Cloud Speech client not initialized")
        
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        try:
            logger.debug(f"Transcribing audio file with Google Cloud: {audio_file_path}")
            
            # Read audio file
            with open(audio_file_path, 'rb') as audio_file:
                content = audio_file.read()
            
            audio = self.speech.RecognitionAudio(content=content)
            
            config = self.speech.RecognitionConfig(
                encoding=self.speech.RecognitionConfig.AudioEncoding.LINEAR16,
                language_code=self.language,
                model=self.model,
                enable_automatic_punctuation=True,
                **kwargs
            )
            
            # Perform transcription
            response = self.client.recognize(config=config, audio=audio)
            
            if not response.results:
                return {
                    "text": "",
                    "language": self.language,
                    "confidence": 0.0,
                    "segments": []
                }
            
            # Extract results
            transcript = ""
            total_confidence = 0.0
            segments = []
            
            for result in response.results:
                alternative = result.alternatives[0]
                transcript += alternative.transcript + " "
                total_confidence += alternative.confidence
                
                if hasattr(alternative, 'words'):
                    for word_info in alternative.words:
                        segments.append({
                            "text": word_info.word,
                            "start": word_info.start_time.total_seconds(),
                            "end": word_info.end_time.total_seconds(),
                            "confidence": alternative.confidence
                        })
            
            avg_confidence = total_confidence / len(response.results) if response.results else 0.0
            
            return {
                "text": transcript.strip(),
                "language": self.language,
                "confidence": avg_confidence,
                "segments": segments
            }
            
        except Exception as e:
            logger.error(f"Error transcribing with Google Cloud: {e}")
            raise
    
    def transcribe_audio_data(self, audio_data: Union[np.ndarray, bytes], 
                             sample_rate: int = 16000, **kwargs) -> Dict[str, Any]:
        """
        Transcribe audio data to text using Google Cloud
        
        Args:
            audio_data: Audio data as numpy array or bytes
            sample_rate: Sample rate of audio data
            **kwargs: Additional Google Cloud options
            
        Returns:
            Dictionary with transcription results
        """
        if not self.client:
            raise RuntimeError("Google Cloud Speech client not initialized")
        
        try:
            logger.debug("Transcribing audio data with Google Cloud")
            
            # Convert numpy array to bytes if needed
            if isinstance(audio_data, np.ndarray):
                import soundfile as sf
                import io
                
                buffer = io.BytesIO()
                sf.write(buffer, audio_data, sample_rate, format='WAV')
                buffer.seek(0)
                audio_bytes = buffer.read()
            else:
                audio_bytes = audio_data
            
            audio = self.speech.RecognitionAudio(content=audio_bytes)
            
            config = self.speech.RecognitionConfig(
                encoding=self.speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=sample_rate,
                language_code=self.language,
                model=self.model,
                enable_automatic_punctuation=True,
                **kwargs
            )
            
            # Perform transcription
            response = self.client.recognize(config=config, audio=audio)
            
            if not response.results:
                return {
                    "text": "",
                    "language": self.language,
                    "confidence": 0.0,
                    "segments": []
                }
            
            # Extract results
            transcript = ""
            total_confidence = 0.0
            segments = []
            
            for result in response.results:
                alternative = result.alternatives[0]
                transcript += alternative.transcript + " "
                total_confidence += alternative.confidence
                
                if hasattr(alternative, 'words'):
                    for word_info in alternative.words:
                        segments.append({
                            "text": word_info.word,
                            "start": word_info.start_time.total_seconds(),
                            "end": word_info.end_time.total_seconds(),
                            "confidence": alternative.confidence
                        })
            
            avg_confidence = total_confidence / len(response.results) if response.results else 0.0
            
            return {
                "text": transcript.strip(),
                "language": self.language,
                "confidence": avg_confidence,
                "segments": segments
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio data with Google Cloud: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Google Cloud Speech is available"""
        return self.client is not None
