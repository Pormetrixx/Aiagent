"""
Text-to-Speech module supporting Coqui TTS and Mimic3
"""
import os
import logging
import numpy as np
from typing import Optional, Dict, Any, Union
from pathlib import Path
import soundfile as sf

logger = logging.getLogger(__name__)


class CoquiTTS:
    """Text-to-Speech using Coqui TTS"""
    
    def __init__(self, model_name: str = "tts_models/de/thorsten/tacotron2-DDC",
                 vocoder: Optional[str] = None, device: str = "cpu"):
        """
        Initialize Coqui TTS
        
        Args:
            model_name: TTS model name
            vocoder: Vocoder model name (optional)
            device: Device to use (cpu, cuda)
        """
        self.model_name = model_name
        self.vocoder = vocoder
        self.device = device
        self.tts = None
        self._load_model()
    
    def _load_model(self):
        """Load the TTS model"""
        try:
            from TTS.api import TTS
            
            logger.info(f"Loading Coqui TTS model: {self.model_name}")
            
            if self.vocoder:
                self.tts = TTS(model_name=self.model_name, vocoder_name=self.vocoder).to(self.device)
            else:
                self.tts = TTS(model_name=self.model_name).to(self.device)
            
            logger.info("Coqui TTS model loaded successfully")
            
        except ImportError:
            logger.error("Coqui TTS not installed. Install with: pip install TTS")
            raise
        except Exception as e:
            logger.error(f"Error loading Coqui TTS model: {e}")
            raise
    
    def synthesize(self, text: str, output_path: Optional[str] = None, 
                   speaker: Optional[str] = None, **kwargs) -> Union[str, np.ndarray]:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            output_path: Output file path (if None, returns audio data)
            speaker: Speaker name/ID for multi-speaker models
            **kwargs: Additional TTS options
            
        Returns:
            Output file path or audio data array
        """
        if not self.tts:
            raise RuntimeError("TTS model not loaded")
        
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            logger.debug(f"Synthesizing text: {text[:50]}...")
            
            # Prepare synthesis arguments
            tts_kwargs = {}
            if speaker:
                tts_kwargs["speaker"] = speaker
            tts_kwargs.update(kwargs)
            
            if output_path:
                # Synthesize to file
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                self.tts.tts_to_file(text=text, file_path=output_path, **tts_kwargs)
                logger.debug(f"Audio synthesized to: {output_path}")
                return output_path
            else:
                # Synthesize to numpy array
                audio_data = self.tts.tts(text=text, **tts_kwargs)
                return np.array(audio_data)
                
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            raise
    
    def get_speakers(self) -> list:
        """Get available speakers for the current model"""
        if not self.tts:
            return []
        
        try:
            return self.tts.speakers if hasattr(self.tts, 'speakers') else []
        except Exception as e:
            logger.error(f"Error getting speakers: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if the TTS system is available"""
        return self.tts is not None


class Mimic3TTS:
    """Text-to-Speech using Mimic3"""
    
    def __init__(self, voice: str = "de_DE/thorsten_low", url: str = "http://localhost:59125"):
        """
        Initialize Mimic3 TTS
        
        Args:
            voice: Voice name for synthesis
            url: Mimic3 server URL
        """
        self.voice = voice
        self.url = url
        self.session = None
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize HTTP session for Mimic3"""
        try:
            import requests
            self.session = requests.Session()
            
            # Test connection
            response = self.session.get(f"{self.url}/api/voices")
            if response.status_code == 200:
                logger.info("Mimic3 TTS connection established")
            else:
                logger.warning(f"Mimic3 server returned status: {response.status_code}")
                
        except ImportError:
            logger.error("requests library not installed")
            raise
        except Exception as e:
            logger.warning(f"Could not connect to Mimic3 server: {e}")
            self.session = None
    
    def synthesize(self, text: str, output_path: Optional[str] = None, **kwargs) -> Union[str, bytes]:
        """
        Synthesize speech from text using Mimic3
        
        Args:
            text: Text to synthesize
            output_path: Output file path (if None, returns audio data)
            **kwargs: Additional synthesis options
            
        Returns:
            Output file path or audio data
        """
        if not self.session:
            raise RuntimeError("Mimic3 session not initialized")
        
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            logger.debug(f"Synthesizing text with Mimic3: {text[:50]}...")
            
            # Prepare request parameters
            params = {
                "voice": self.voice,
                **kwargs
            }
            
            # Make synthesis request
            response = self.session.post(
                f"{self.url}/api/tts",
                data={"text": text},
                params=params,
                headers={"Accept": "audio/wav"}
            )
            
            if response.status_code == 200:
                audio_data = response.content
                
                if output_path:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(audio_data)
                    logger.debug(f"Audio synthesized to: {output_path}")
                    return output_path
                else:
                    return audio_data
            else:
                raise RuntimeError(f"Mimic3 synthesis failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error synthesizing with Mimic3: {e}")
            raise
    
    def get_voices(self) -> list:
        """Get available voices from Mimic3 server"""
        if not self.session:
            return []
        
        try:
            response = self.session.get(f"{self.url}/api/voices")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Error getting Mimic3 voices: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if Mimic3 is available"""
        return self.session is not None


class TTSEngine:
    """Unified TTS engine interface"""
    
    def __init__(self, engine_type: str = "coqui", **config):
        """
        Initialize TTS engine
        
        Args:
            engine_type: Type of TTS engine (coqui, mimic3)
            **config: Engine-specific configuration
        """
        self.engine_type = engine_type.lower()
        self.config = config
        self.engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the appropriate TTS engine"""
        try:
            if self.engine_type == "coqui":
                self.engine = CoquiTTS(**self.config)
            elif self.engine_type == "mimic3":
                self.engine = Mimic3TTS(**self.config)
            else:
                raise ValueError(f"Unsupported TTS engine: {self.engine_type}")
                
        except Exception as e:
            logger.error(f"Failed to initialize {self.engine_type} TTS engine: {e}")
            raise
    
    def synthesize(self, text: str, output_path: Optional[str] = None, **kwargs) -> Union[str, np.ndarray, bytes]:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            output_path: Output file path
            **kwargs: Additional options
            
        Returns:
            Output path or audio data
        """
        if not self.engine:
            raise RuntimeError("TTS engine not initialized")
        
        return self.engine.synthesize(text, output_path, **kwargs)
    
    def is_available(self) -> bool:
        """Check if TTS engine is available"""
        return self.engine and self.engine.is_available()
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about the current engine"""
        info = {
            "type": self.engine_type,
            "available": self.is_available(),
            "config": self.config
        }
        
        if self.engine_type == "coqui" and hasattr(self.engine, 'get_speakers'):
            info["speakers"] = self.engine.get_speakers()
        elif self.engine_type == "mimic3" and hasattr(self.engine, 'get_voices'):
            info["voices"] = self.engine.get_voices()
        
        return info


def create_tts_engine(config: Dict[str, Any]) -> TTSEngine:
    """
    Factory function to create TTS engine based on configuration
    
    Args:
        config: TTS configuration dictionary
        
    Returns:
        Configured TTS engine
    """
    engine_type = config.get("engine", "coqui").lower()
    
    if engine_type == "coqui":
        engine_config = {
            "model_name": config.get("model_name", "tts_models/de/thorsten/tacotron2-DDC"),
            "vocoder": config.get("vocoder"),
            "device": config.get("device", "cpu")
        }
    elif engine_type == "mimic3":
        engine_config = {
            "voice": config.get("voice", "de_DE/thorsten_low"),
            "url": config.get("url", "http://localhost:59125")
        }
    else:
        raise ValueError(f"Unsupported TTS engine: {engine_type}")
    
    return TTSEngine(engine_type, **engine_config)


class AudioPostProcessor:
    """Post-processing utilities for synthesized audio"""
    
    @staticmethod
    def adjust_speed(audio_data: np.ndarray, speed_factor: float) -> np.ndarray:
        """
        Adjust audio playback speed
        
        Args:
            audio_data: Input audio data
            speed_factor: Speed multiplier (1.0 = normal, >1.0 = faster, <1.0 = slower)
            
        Returns:
            Speed-adjusted audio data
        """
        try:
            import librosa
            return librosa.effects.time_stretch(audio_data, rate=speed_factor)
        except ImportError:
            logger.warning("librosa not available for speed adjustment")
            return audio_data
        except Exception as e:
            logger.error(f"Error adjusting audio speed: {e}")
            return audio_data
    
    @staticmethod
    def adjust_pitch(audio_data: np.ndarray, sample_rate: int, pitch_shift: float) -> np.ndarray:
        """
        Adjust audio pitch
        
        Args:
            audio_data: Input audio data
            sample_rate: Audio sample rate
            pitch_shift: Pitch shift in semitones
            
        Returns:
            Pitch-adjusted audio data
        """
        try:
            import librosa
            return librosa.effects.pitch_shift(audio_data, sr=sample_rate, n_steps=pitch_shift)
        except ImportError:
            logger.warning("librosa not available for pitch adjustment")
            return audio_data
        except Exception as e:
            logger.error(f"Error adjusting audio pitch: {e}")
            return audio_data
    
    @staticmethod
    def apply_volume(audio_data: np.ndarray, volume_factor: float) -> np.ndarray:
        """
        Apply volume adjustment
        
        Args:
            audio_data: Input audio data
            volume_factor: Volume multiplier
            
        Returns:
            Volume-adjusted audio data
        """
        adjusted = audio_data * volume_factor
        
        # Prevent clipping
        max_val = np.abs(adjusted).max()
        if max_val > 1.0:
            adjusted = adjusted / max_val
        
        return adjusted