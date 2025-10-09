"""
Speech-to-Text using Deepgram API
"""
import os
import logging
from typing import Dict, Any, Union, Optional
import numpy as np
from pathlib import Path
from .base import BaseSTTEngine

logger = logging.getLogger(__name__)


class DeepgramSTT(BaseSTTEngine):
    """Speech-to-Text using Deepgram API"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Deepgram STT
        
        Args:
            config: Configuration dictionary with:
                - api_key: Deepgram API key
                - model: Model to use (default: nova-2)
                - language: Language code (default: de)
        """
        super().__init__(config)
        self.api_key = config.get("api_key") or os.getenv("DEEPGRAM_API_KEY")
        self.model = config.get("model", "nova-2")
        self.client = None
        
        if not self.api_key:
            logger.warning("Deepgram API key not provided")
        else:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Deepgram client"""
        try:
            from deepgram import DeepgramClient, PrerecordedOptions, FileSource
            
            self.client = DeepgramClient(self.api_key)
            self.PrerecordedOptions = PrerecordedOptions
            self.FileSource = FileSource
            
            logger.info("Deepgram client initialized successfully")
            
        except ImportError:
            logger.error("Deepgram SDK not installed. Install with: pip install deepgram-sdk")
            self.client = None
        except Exception as e:
            logger.error(f"Error initializing Deepgram client: {e}")
            self.client = None
    
    def transcribe_file(self, audio_file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Transcribe audio file to text using Deepgram
        
        Args:
            audio_file_path: Path to audio file
            **kwargs: Additional Deepgram options
            
        Returns:
            Dictionary with transcription results
        """
        if not self.client:
            raise RuntimeError("Deepgram client not initialized")
        
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        try:
            logger.debug(f"Transcribing audio file with Deepgram: {audio_file_path}")
            
            # Read audio file
            with open(audio_file_path, 'rb') as audio:
                buffer_data = audio.read()
            
            payload = self.FileSource(buffer_data)
            
            # Configure options
            options = self.PrerecordedOptions(
                model=self.model,
                language=self.language,
                smart_format=True,
                punctuate=True,
                **kwargs
            )
            
            # Transcribe
            response = self.client.listen.prerecorded.v("1").transcribe_file(
                payload, options
            )
            
            # Extract results
            transcript = response.results.channels[0].alternatives[0]
            
            return {
                "text": transcript.transcript.strip(),
                "language": self.language,
                "confidence": transcript.confidence,
                "segments": self._extract_segments(response)
            }
            
        except Exception as e:
            logger.error(f"Error transcribing with Deepgram: {e}")
            raise
    
    def transcribe_audio_data(self, audio_data: Union[np.ndarray, bytes], 
                             sample_rate: int = 16000, **kwargs) -> Dict[str, Any]:
        """
        Transcribe audio data to text using Deepgram
        
        Args:
            audio_data: Audio data as numpy array or bytes
            sample_rate: Sample rate of audio data
            **kwargs: Additional Deepgram options
            
        Returns:
            Dictionary with transcription results
        """
        if not self.client:
            raise RuntimeError("Deepgram client not initialized")
        
        try:
            logger.debug("Transcribing audio data with Deepgram")
            
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
            
            payload = self.FileSource(audio_bytes)
            
            # Configure options
            options = self.PrerecordedOptions(
                model=self.model,
                language=self.language,
                smart_format=True,
                punctuate=True,
                **kwargs
            )
            
            # Transcribe
            response = self.client.listen.prerecorded.v("1").transcribe_file(
                payload, options
            )
            
            # Extract results
            transcript = response.results.channels[0].alternatives[0]
            
            return {
                "text": transcript.transcript.strip(),
                "language": self.language,
                "confidence": transcript.confidence,
                "segments": self._extract_segments(response)
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio data with Deepgram: {e}")
            raise
    
    def _extract_segments(self, response) -> list:
        """Extract word-level segments from Deepgram response"""
        try:
            words = response.results.channels[0].alternatives[0].words
            segments = []
            
            for word in words:
                segments.append({
                    "text": word.word,
                    "start": word.start,
                    "end": word.end,
                    "confidence": word.confidence
                })
            
            return segments
        except Exception as e:
            logger.debug(f"Could not extract segments: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if Deepgram is available"""
        return self.client is not None and self.api_key is not None
