"""
Speech processing module for the AI Cold Calling Agent
"""
from .stt import WhisperSTT, AudioProcessor, create_stt_engine
from .tts import CoquiTTS, Mimic3TTS, TTSEngine, create_tts_engine, AudioPostProcessor

__all__ = [
    'WhisperSTT', 'AudioProcessor', 'create_stt_engine',
    'CoquiTTS', 'Mimic3TTS', 'TTSEngine', 'create_tts_engine', 
    'AudioPostProcessor'
]