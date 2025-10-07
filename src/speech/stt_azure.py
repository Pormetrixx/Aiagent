"""
Speech-to-Text using Azure Speech Services
"""
import os
import logging
from typing import Dict, Any, Union, Optional
import numpy as np
from pathlib import Path
from .base import BaseSTTEngine

logger = logging.getLogger(__name__)


class AzureSTT(BaseSTTEngine):
    """Speech-to-Text using Azure Speech Services"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Azure STT
        
        Args:
            config: Configuration dictionary with:
                - api_key: Azure Speech API key
                - region: Azure region (e.g., westeurope)
                - language: Language code (default: de-DE)
        """
        super().__init__(config)
        self.api_key = config.get("api_key") or os.getenv("AZURE_SPEECH_KEY")
        self.region = config.get("region") or os.getenv("AZURE_SPEECH_REGION", "westeurope")
        self.speech_config = None
        
        # Azure uses de-DE format instead of just de
        if self.language == "de":
            self.language = "de-DE"
        
        if not self.api_key:
            logger.warning("Azure Speech API key not provided")
        else:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Azure Speech client"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            self.speechsdk = speechsdk
            self.speech_config = speechsdk.SpeechConfig(
                subscription=self.api_key,
                region=self.region
            )
            self.speech_config.speech_recognition_language = self.language
            
            logger.info("Azure Speech client initialized successfully")
            
        except ImportError:
            logger.error("Azure Speech SDK not installed. Install with: pip install azure-cognitiveservices-speech")
            self.speech_config = None
        except Exception as e:
            logger.error(f"Error initializing Azure Speech client: {e}")
            self.speech_config = None
    
    def transcribe_file(self, audio_file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Transcribe audio file to text using Azure
        
        Args:
            audio_file_path: Path to audio file
            **kwargs: Additional Azure options
            
        Returns:
            Dictionary with transcription results
        """
        if not self.speech_config:
            raise RuntimeError("Azure Speech client not initialized")
        
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        try:
            logger.debug(f"Transcribing audio file with Azure: {audio_file_path}")
            
            # Create audio config from file
            audio_config = self.speechsdk.audio.AudioConfig(filename=audio_file_path)
            
            # Create speech recognizer
            speech_recognizer = self.speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # Perform recognition
            result = speech_recognizer.recognize_once()
            
            if result.reason == self.speechsdk.ResultReason.RecognizedSpeech:
                return {
                    "text": result.text.strip(),
                    "language": self.language,
                    "confidence": self._get_confidence(result),
                    "segments": []
                }
            elif result.reason == self.speechsdk.ResultReason.NoMatch:
                logger.warning("Azure: No speech could be recognized")
                return {
                    "text": "",
                    "language": self.language,
                    "confidence": 0.0,
                    "segments": []
                }
            elif result.reason == self.speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                logger.error(f"Azure recognition canceled: {cancellation.reason}")
                if cancellation.reason == self.speechsdk.CancellationReason.Error:
                    logger.error(f"Error details: {cancellation.error_details}")
                raise RuntimeError(f"Azure recognition error: {cancellation.error_details}")
            
        except Exception as e:
            logger.error(f"Error transcribing with Azure: {e}")
            raise
    
    def transcribe_audio_data(self, audio_data: Union[np.ndarray, bytes], 
                             sample_rate: int = 16000, **kwargs) -> Dict[str, Any]:
        """
        Transcribe audio data to text using Azure
        
        Args:
            audio_data: Audio data as numpy array or bytes
            sample_rate: Sample rate of audio data
            **kwargs: Additional Azure options
            
        Returns:
            Dictionary with transcription results
        """
        if not self.speech_config:
            raise RuntimeError("Azure Speech client not initialized")
        
        try:
            logger.debug("Transcribing audio data with Azure")
            
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
            
            # Create push stream
            push_stream = self.speechsdk.audio.PushAudioInputStream()
            audio_config = self.speechsdk.audio.AudioConfig(stream=push_stream)
            
            # Create speech recognizer
            speech_recognizer = self.speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # Write audio data to stream
            push_stream.write(audio_bytes)
            push_stream.close()
            
            # Perform recognition
            result = speech_recognizer.recognize_once()
            
            if result.reason == self.speechsdk.ResultReason.RecognizedSpeech:
                return {
                    "text": result.text.strip(),
                    "language": self.language,
                    "confidence": self._get_confidence(result),
                    "segments": []
                }
            elif result.reason == self.speechsdk.ResultReason.NoMatch:
                logger.warning("Azure: No speech could be recognized")
                return {
                    "text": "",
                    "language": self.language,
                    "confidence": 0.0,
                    "segments": []
                }
            else:
                raise RuntimeError(f"Azure recognition failed: {result.reason}")
            
        except Exception as e:
            logger.error(f"Error transcribing audio data with Azure: {e}")
            raise
    
    def _get_confidence(self, result) -> float:
        """Extract confidence score from Azure result"""
        try:
            # Azure doesn't provide direct confidence in the basic result
            # Would need to use detailed results for confidence
            return 0.9  # Default high confidence if recognized
        except Exception:
            return 0.0
    
    def is_available(self) -> bool:
        """Check if Azure Speech is available"""
        return self.speech_config is not None and self.api_key is not None
