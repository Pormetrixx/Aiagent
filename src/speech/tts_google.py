"""
Text-to-Speech using Google Cloud Text-to-Speech
"""
import os
import logging
from typing import Dict, Any, Union, Optional
import numpy as np
from pathlib import Path
from .base import BaseTTSEngine

logger = logging.getLogger(__name__)


class GoogleTTS(BaseTTSEngine):
    """Text-to-Speech using Google Cloud Text-to-Speech"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Google Cloud TTS
        
        Args:
            config: Configuration dictionary with:
                - credentials_path: Path to Google Cloud credentials JSON
                - voice: Voice name (default: de-DE-Wavenet-C)
                - language: Language code (default: de-DE)
        """
        super().__init__(config)
        self.credentials_path = config.get("credentials_path") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.voice = config.get("voice", "de-DE-Wavenet-C")  # German female voice
        self.client = None
        
        # Google uses de-DE format instead of just de
        if self.language == "de":
            self.language = "de-DE"
        
        if not self.credentials_path:
            logger.warning("Google Cloud credentials not provided")
        else:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Cloud TTS client"""
        try:
            from google.cloud import texttospeech
            
            # Set credentials environment variable if not already set
            if self.credentials_path and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path
            
            self.client = texttospeech.TextToSpeechClient()
            self.texttospeech = texttospeech
            
            logger.info("Google Cloud TTS initialized successfully")
            
        except ImportError:
            logger.error("Google Cloud TTS not installed. Install with: pip install google-cloud-texttospeech")
            self.client = None
        except Exception as e:
            logger.error(f"Error initializing Google Cloud TTS: {e}")
            self.client = None
    
    def synthesize(self, text: str, output_path: Optional[str] = None, 
                   **kwargs) -> Union[str, bytes]:
        """
        Synthesize speech from text using Google Cloud
        
        Args:
            text: Text to synthesize
            output_path: Output file path (if None, returns audio data)
            **kwargs: Additional Google Cloud options:
                - voice: Override default voice
                - speaking_rate: Speaking rate (0.25 to 4.0)
                - pitch: Speaking pitch (-20.0 to 20.0)
            
        Returns:
            Output file path or audio data bytes
        """
        if not self.client:
            raise RuntimeError("Google Cloud TTS not initialized")
        
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            logger.debug(f"Synthesizing text with Google Cloud: {text[:50]}...")
            
            # Set the text input to be synthesized
            synthesis_input = self.texttospeech.SynthesisInput(text=text)
            
            # Use custom voice if provided
            voice_name = kwargs.get("voice", self.voice)
            
            # Build the voice request
            voice = self.texttospeech.VoiceSelectionParams(
                language_code=self.language,
                name=voice_name
            )
            
            # Select the type of audio file
            audio_config = self.texttospeech.AudioConfig(
                audio_encoding=self.texttospeech.AudioEncoding.LINEAR16,
                speaking_rate=kwargs.get("speaking_rate", 1.0),
                pitch=kwargs.get("pitch", 0.0)
            )
            
            # Perform the text-to-speech request
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            audio_data = response.audio_content
            
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as out:
                    out.write(audio_data)
                logger.debug(f"Audio synthesized to: {output_path}")
                return output_path
            else:
                return audio_data
                
        except Exception as e:
            logger.error(f"Error synthesizing with Google Cloud: {e}")
            raise
    
    def get_voices(self) -> list:
        """Get available voices from Google Cloud"""
        if not self.client:
            return []
        
        try:
            # Performs the list voices request
            response = self.client.list_voices()
            
            voices = []
            for voice in response.voices:
                # Filter for the target language
                if self.language.split("-")[0] in str(voice.language_codes):
                    voices.append({
                        "name": voice.name,
                        "language_codes": list(voice.language_codes),
                        "ssml_gender": voice.ssml_gender.name,
                        "natural_sample_rate_hertz": voice.natural_sample_rate_hertz
                    })
            
            return voices
            
        except Exception as e:
            logger.error(f"Error getting Google Cloud voices: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if Google Cloud TTS is available"""
        return self.client is not None
