"""
Base classes for Speech-to-Text and Text-to-Speech engines
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
import numpy as np
import logging

logger = logging.getLogger(__name__)


class BaseSTTEngine(ABC):
    """Abstract base class for Speech-to-Text engines"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize STT engine
        
        Args:
            config: Engine configuration dictionary
        """
        self.config = config
        self.language = config.get("language", "de")
    
    @abstractmethod
    def transcribe_file(self, audio_file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Transcribe audio file to text
        
        Args:
            audio_file_path: Path to audio file
            **kwargs: Additional engine-specific options
            
        Returns:
            Dictionary with transcription results:
            {
                "text": str,
                "language": str,
                "confidence": float,
                "segments": list (optional)
            }
        """
        pass
    
    @abstractmethod
    def transcribe_audio_data(self, audio_data: Union[np.ndarray, bytes], 
                             sample_rate: int = 16000, **kwargs) -> Dict[str, Any]:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Audio data as numpy array or bytes
            sample_rate: Sample rate of audio data
            **kwargs: Additional engine-specific options
            
        Returns:
            Dictionary with transcription results
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the STT engine is available and ready
        
        Returns:
            True if engine is ready, False otherwise
        """
        pass
    
    def get_engine_info(self) -> Dict[str, Any]:
        """
        Get information about the engine
        
        Returns:
            Dictionary with engine information
        """
        return {
            "type": self.__class__.__name__,
            "language": self.language,
            "available": self.is_available(),
            "config": self.config
        }


class BaseTTSEngine(ABC):
    """Abstract base class for Text-to-Speech engines"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize TTS engine
        
        Args:
            config: Engine configuration dictionary
        """
        self.config = config
        self.language = config.get("language", "de")
        self.voice = config.get("voice")
    
    @abstractmethod
    def synthesize(self, text: str, output_path: Optional[str] = None, 
                   **kwargs) -> Union[str, np.ndarray, bytes]:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            output_path: Output file path (if None, returns audio data)
            **kwargs: Additional engine-specific options
            
        Returns:
            Output file path or audio data
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the TTS engine is available and ready
        
        Returns:
            True if engine is ready, False otherwise
        """
        pass
    
    def get_voices(self) -> list:
        """
        Get available voices for the engine
        
        Returns:
            List of available voices
        """
        return []
    
    def get_engine_info(self) -> Dict[str, Any]:
        """
        Get information about the engine
        
        Returns:
            Dictionary with engine information
        """
        info = {
            "type": self.__class__.__name__,
            "language": self.language,
            "voice": self.voice,
            "available": self.is_available(),
            "config": self.config
        }
        
        voices = self.get_voices()
        if voices:
            info["voices"] = voices
        
        return info
