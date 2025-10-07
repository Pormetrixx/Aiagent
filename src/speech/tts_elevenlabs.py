"""
Text-to-Speech using ElevenLabs API
"""
import os
import logging
from typing import Dict, Any, Union, Optional
import numpy as np
from pathlib import Path
from .base import BaseTTSEngine

logger = logging.getLogger(__name__)


class ElevenLabsTTS(BaseTTSEngine):
    """Text-to-Speech using ElevenLabs API"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ElevenLabs TTS
        
        Args:
            config: Configuration dictionary with:
                - api_key: ElevenLabs API key
                - voice_id: Voice ID to use (or voice name)
                - model: Model to use (default: eleven_multilingual_v2)
                - language: Language code (default: de)
        """
        super().__init__(config)
        self.api_key = config.get("api_key") or os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = config.get("voice_id", "21m00Tcm4TlvDq8ikWAM")  # Default: Rachel
        self.model = config.get("model", "eleven_multilingual_v2")
        self.client = None
        
        if not self.api_key:
            logger.warning("ElevenLabs API key not provided")
        else:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ElevenLabs client"""
        try:
            from elevenlabs.client import ElevenLabs
            from elevenlabs import VoiceSettings
            
            self.client = ElevenLabs(api_key=self.api_key)
            self.VoiceSettings = VoiceSettings
            
            logger.info("ElevenLabs client initialized successfully")
            
        except ImportError:
            logger.error("ElevenLabs SDK not installed. Install with: pip install elevenlabs")
            self.client = None
        except Exception as e:
            logger.error(f"Error initializing ElevenLabs client: {e}")
            self.client = None
    
    def synthesize(self, text: str, output_path: Optional[str] = None, 
                   **kwargs) -> Union[str, bytes]:
        """
        Synthesize speech from text using ElevenLabs
        
        Args:
            text: Text to synthesize
            output_path: Output file path (if None, returns audio data)
            **kwargs: Additional ElevenLabs options:
                - stability: Voice stability (0.0-1.0)
                - similarity_boost: Voice similarity boost (0.0-1.0)
                - style: Style exaggeration (0.0-1.0)
                - use_speaker_boost: Enable speaker boost
            
        Returns:
            Output file path or audio data bytes
        """
        if not self.client:
            raise RuntimeError("ElevenLabs client not initialized")
        
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            logger.debug(f"Synthesizing text with ElevenLabs: {text[:50]}...")
            
            # Configure voice settings
            voice_settings = self.VoiceSettings(
                stability=kwargs.get("stability", 0.5),
                similarity_boost=kwargs.get("similarity_boost", 0.75),
                style=kwargs.get("style", 0.0),
                use_speaker_boost=kwargs.get("use_speaker_boost", True)
            )
            
            # Generate speech
            audio_generator = self.client.generate(
                text=text,
                voice=self.voice_id,
                model=self.model,
                voice_settings=voice_settings
            )
            
            # Collect audio chunks
            audio_chunks = []
            for chunk in audio_generator:
                if chunk:
                    audio_chunks.append(chunk)
            
            audio_data = b''.join(audio_chunks)
            
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(audio_data)
                logger.debug(f"Audio synthesized to: {output_path}")
                return output_path
            else:
                return audio_data
                
        except Exception as e:
            logger.error(f"Error synthesizing with ElevenLabs: {e}")
            raise
    
    def get_voices(self) -> list:
        """Get available voices from ElevenLabs"""
        if not self.client:
            return []
        
        try:
            response = self.client.voices.get_all()
            voices = []
            
            for voice in response.voices:
                voices.append({
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": voice.category,
                    "description": getattr(voice, 'description', ''),
                    "labels": getattr(voice, 'labels', {})
                })
            
            return voices
            
        except Exception as e:
            logger.error(f"Error getting ElevenLabs voices: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if ElevenLabs is available"""
        return self.client is not None and self.api_key is not None
