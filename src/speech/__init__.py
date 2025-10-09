"""
Speech processing module for the AI Cold Calling Agent
"""
from .base import BaseSTTEngine, BaseTTSEngine
from .stt import WhisperSTT, AudioProcessor, create_stt_engine
from .tts import CoquiTTS, Mimic3TTS, TTSEngine, create_tts_engine, AudioPostProcessor

__all__ = [
    'BaseSTTEngine', 'BaseTTSEngine',
    'WhisperSTT', 'AudioProcessor', 'create_stt_engine',
    'CoquiTTS', 'Mimic3TTS', 'TTSEngine', 'create_tts_engine', 
    'AudioPostProcessor'
]