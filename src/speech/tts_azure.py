"""
Text-to-Speech using Azure Speech Services
"""
import os
import logging
from typing import Dict, Any, Union, Optional
import numpy as np
from pathlib import Path
from .base import BaseTTSEngine

logger = logging.getLogger(__name__)


class AzureTTS(BaseTTSEngine):
    """Text-to-Speech using Azure Speech Services"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Azure TTS
        
        Args:
            config: Configuration dictionary with:
                - api_key: Azure Speech API key
                - region: Azure region (e.g., westeurope)
                - voice: Voice name (default: de-DE-KatjaNeural)
                - language: Language code (default: de-DE)
        """
        super().__init__(config)
        self.api_key = config.get("api_key") or os.getenv("AZURE_SPEECH_KEY")
        self.region = config.get("region") or os.getenv("AZURE_SPEECH_REGION", "westeurope")
        self.voice = config.get("voice", "de-DE-KatjaNeural")  # German female voice
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
            self.speech_config.speech_synthesis_voice_name = self.voice
            
            logger.info("Azure TTS initialized successfully")
            
        except ImportError:
            logger.error("Azure Speech SDK not installed. Install with: pip install azure-cognitiveservices-speech")
            self.speech_config = None
        except Exception as e:
            logger.error(f"Error initializing Azure TTS: {e}")
            self.speech_config = None
    
    def synthesize(self, text: str, output_path: Optional[str] = None, 
                   **kwargs) -> Union[str, bytes]:
        """
        Synthesize speech from text using Azure
        
        Args:
            text: Text to synthesize
            output_path: Output file path (if None, returns audio data)
            **kwargs: Additional Azure options:
                - voice: Override default voice
                - rate: Speech rate (e.g., "+10%", "-10%")
                - pitch: Speech pitch (e.g., "+5%", "-5%")
            
        Returns:
            Output file path or audio data bytes
        """
        if not self.speech_config:
            raise RuntimeError("Azure TTS not initialized")
        
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            logger.debug(f"Synthesizing text with Azure: {text[:50]}...")
            
            # Use custom voice if provided
            voice = kwargs.get("voice", self.voice)
            
            # Create SSML if rate or pitch specified
            if kwargs.get("rate") or kwargs.get("pitch"):
                ssml_text = self._create_ssml(text, voice, **kwargs)
            else:
                ssml_text = None
            
            if output_path:
                # Synthesize to file
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                audio_config = self.speechsdk.audio.AudioOutputConfig(filename=output_path)
                
                synthesizer = self.speechsdk.SpeechSynthesizer(
                    speech_config=self.speech_config,
                    audio_config=audio_config
                )
                
                if ssml_text:
                    result = synthesizer.speak_ssml_async(ssml_text).get()
                else:
                    result = synthesizer.speak_text_async(text).get()
                
                if result.reason == self.speechsdk.ResultReason.SynthesizingAudioCompleted:
                    logger.debug(f"Audio synthesized to: {output_path}")
                    return output_path
                else:
                    raise RuntimeError(f"Azure TTS failed: {result.reason}")
            else:
                # Synthesize to memory
                synthesizer = self.speechsdk.SpeechSynthesizer(
                    speech_config=self.speech_config,
                    audio_config=None
                )
                
                if ssml_text:
                    result = synthesizer.speak_ssml_async(ssml_text).get()
                else:
                    result = synthesizer.speak_text_async(text).get()
                
                if result.reason == self.speechsdk.ResultReason.SynthesizingAudioCompleted:
                    return result.audio_data
                else:
                    raise RuntimeError(f"Azure TTS failed: {result.reason}")
                
        except Exception as e:
            logger.error(f"Error synthesizing with Azure: {e}")
            raise
    
    def _create_ssml(self, text: str, voice: str, **kwargs) -> str:
        """Create SSML markup for advanced synthesis options"""
        rate = kwargs.get("rate", "0%")
        pitch = kwargs.get("pitch", "0%")
        
        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{self.language}">
            <voice name="{voice}">
                <prosody rate="{rate}" pitch="{pitch}">
                    {text}
                </prosody>
            </voice>
        </speak>
        """
        return ssml.strip()
    
    def get_voices(self) -> list:
        """Get available voices from Azure"""
        if not self.speech_config:
            return []
        
        try:
            synthesizer = self.speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=None
            )
            
            result = synthesizer.get_voices_async().get()
            
            voices = []
            for voice in result.voices:
                if self.language.split("-")[0] in voice.locale.lower():
                    voices.append({
                        "name": voice.short_name,
                        "locale": voice.locale,
                        "gender": voice.gender.name,
                        "voice_type": voice.voice_type.name
                    })
            
            return voices
            
        except Exception as e:
            logger.error(f"Error getting Azure voices: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if Azure TTS is available"""
        return self.speech_config is not None and self.api_key is not None
