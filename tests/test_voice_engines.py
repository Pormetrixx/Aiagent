#!/usr/bin/env python3
"""
Test script for all Speech-to-Text and Text-to-Speech engines
Tests each configured engine and provides diagnostic information
"""
import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.speech import create_stt_engine, create_tts_engine
from src.config import ConfigManager

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Test text for TTS (German)
TEST_TEXT_GERMAN = """
Guten Tag, ich bin Ihr KI-Assistent für Kaltakquise. 
Ich kann Ihnen dabei helfen, qualifizierte Leads zu generieren und Termine zu vereinbaren. 
Lassen Sie uns gemeinsam Ihre Investitionsziele besprechen.
"""

def test_stt_engine(engine_name: str, config: dict):
    """Test a Speech-to-Text engine"""
    print(f"\n{'='*60}")
    print(f"Testing STT Engine: {engine_name.upper()}")
    print(f"{'='*60}")
    
    try:
        # Create engine
        stt = create_stt_engine(config)
        
        # Check availability
        if not stt.is_available():
            print(f"❌ {engine_name} STT is NOT available")
            print("   Check configuration and API keys")
            return False
        
        print(f"✅ {engine_name} STT is available")
        
        # Get engine info
        info = stt.get_engine_info()
        print(f"   Type: {info['type']}")
        print(f"   Language: {info.get('language', 'N/A')}")
        
        # Test with sample audio if available
        test_audio_path = Path(__file__).parent.parent / "recordings" / "test_audio.wav"
        if test_audio_path.exists():
            print(f"\n   Testing transcription with: {test_audio_path}")
            try:
                result = stt.transcribe_file(str(test_audio_path))
                print(f"   📝 Transcription: {result['text'][:100]}...")
                print(f"   📊 Confidence: {result.get('confidence', 0):.2%}")
            except Exception as e:
                print(f"   ⚠️  Transcription test failed: {e}")
        else:
            print(f"   ℹ️  No test audio file found at {test_audio_path}")
            print(f"   Create one to test transcription functionality")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize {engine_name} STT: {e}")
        return False


def test_tts_engine(engine_name: str, config: dict):
    """Test a Text-to-Speech engine"""
    print(f"\n{'='*60}")
    print(f"Testing TTS Engine: {engine_name.upper()}")
    print(f"{'='*60}")
    
    try:
        # Create engine
        tts = create_tts_engine(config)
        
        # Check availability
        if not tts.is_available():
            print(f"❌ {engine_name} TTS is NOT available")
            print("   Check configuration and API keys")
            return False
        
        print(f"✅ {engine_name} TTS is available")
        
        # Get engine info
        info = tts.get_engine_info()
        print(f"   Type: {info['type']}")
        print(f"   Language: {info.get('language', 'N/A')}")
        print(f"   Voice: {info.get('voice', 'N/A')}")
        
        # List available voices
        voices = tts.get_voices()
        if voices:
            print(f"   📢 Available voices: {len(voices)}")
            for i, voice in enumerate(voices[:3]):  # Show first 3
                if isinstance(voice, dict):
                    voice_name = voice.get('name', voice.get('voice_id', 'Unknown'))
                    print(f"      {i+1}. {voice_name}")
            if len(voices) > 3:
                print(f"      ... and {len(voices) - 3} more")
        
        # Test synthesis
        output_dir = Path(__file__).parent.parent / "recordings" / "test_output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"test_{engine_name}.wav"
        
        print(f"\n   Testing synthesis...")
        print(f"   Output: {output_path}")
        
        try:
            result = tts.synthesize(TEST_TEXT_GERMAN, str(output_path))
            print(f"   ✅ Audio synthesized successfully")
            print(f"   📁 File size: {output_path.stat().st_size / 1024:.2f} KB")
        except Exception as e:
            print(f"   ⚠️  Synthesis test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize {engine_name} TTS: {e}")
        return False


def main():
    """Main test function"""
    print("="*60)
    print("AI Cold Calling Agent - Voice Engine Test Suite")
    print("="*60)
    
    # Load configuration
    config_manager = ConfigManager()
    
    # Test STT Engines
    print("\n" + "="*60)
    print("SPEECH-TO-TEXT ENGINES")
    print("="*60)
    
    stt_results = {}
    
    # Whisper (local)
    whisper_config = {
        "engine": "whisper",
        "model_size": os.getenv("STT_WHISPER_MODEL_SIZE", "base"),
        "device": os.getenv("STT_WHISPER_DEVICE", "cpu"),
        "language": os.getenv("STT_LANGUAGE", "de")
    }
    stt_results["whisper"] = test_stt_engine("whisper", whisper_config)
    
    # Deepgram
    if os.getenv("DEEPGRAM_API_KEY"):
        deepgram_config = {
            "engine": "deepgram",
            "api_key": os.getenv("DEEPGRAM_API_KEY"),
            "model": os.getenv("STT_DEEPGRAM_MODEL", "nova-2"),
            "language": os.getenv("STT_LANGUAGE", "de")
        }
        stt_results["deepgram"] = test_stt_engine("deepgram", deepgram_config)
    else:
        print("\n⏭️  Skipping Deepgram (no API key)")
    
    # Azure
    if os.getenv("AZURE_SPEECH_KEY"):
        azure_config = {
            "engine": "azure",
            "api_key": os.getenv("AZURE_SPEECH_KEY"),
            "region": os.getenv("AZURE_SPEECH_REGION", "westeurope"),
            "language": "de-DE"
        }
        stt_results["azure"] = test_stt_engine("azure", azure_config)
    else:
        print("\n⏭️  Skipping Azure STT (no API key)")
    
    # Google
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        google_config = {
            "engine": "google",
            "credentials_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            "model": os.getenv("STT_GOOGLE_MODEL", "latest_long"),
            "language": "de-DE"
        }
        stt_results["google"] = test_stt_engine("google", google_config)
    else:
        print("\n⏭️  Skipping Google STT (no credentials)")
    
    # Test TTS Engines
    print("\n" + "="*60)
    print("TEXT-TO-SPEECH ENGINES")
    print("="*60)
    
    tts_results = {}
    
    # Coqui (local)
    coqui_config = {
        "engine": "coqui",
        "model_name": os.getenv("TTS_COQUI_MODEL", "tts_models/de/thorsten/tacotron2-DDC"),
        "vocoder": os.getenv("TTS_COQUI_VOCODER"),
        "device": os.getenv("TTS_COQUI_DEVICE", "cpu"),
        "language": "de"
    }
    tts_results["coqui"] = test_tts_engine("coqui", coqui_config)
    
    # Mimic3 (local server)
    mimic3_config = {
        "engine": "mimic3",
        "voice": os.getenv("TTS_MIMIC3_VOICE", "de_DE/thorsten_low"),
        "url": os.getenv("TTS_MIMIC3_URL", "http://localhost:59125"),
        "language": "de"
    }
    tts_results["mimic3"] = test_tts_engine("mimic3", mimic3_config)
    
    # ElevenLabs
    if os.getenv("ELEVENLABS_API_KEY"):
        elevenlabs_config = {
            "engine": "elevenlabs",
            "api_key": os.getenv("ELEVENLABS_API_KEY"),
            "voice_id": os.getenv("TTS_ELEVENLABS_VOICE_ID"),
            "model": os.getenv("TTS_ELEVENLABS_MODEL", "eleven_multilingual_v2"),
            "language": "de"
        }
        tts_results["elevenlabs"] = test_tts_engine("elevenlabs", elevenlabs_config)
    else:
        print("\n⏭️  Skipping ElevenLabs (no API key)")
    
    # Azure TTS
    if os.getenv("AZURE_SPEECH_KEY"):
        azure_tts_config = {
            "engine": "azure",
            "api_key": os.getenv("AZURE_SPEECH_KEY"),
            "region": os.getenv("AZURE_SPEECH_REGION", "westeurope"),
            "voice": os.getenv("TTS_AZURE_VOICE", "de-DE-KatjaNeural"),
            "language": "de-DE"
        }
        tts_results["azure"] = test_tts_engine("azure", azure_tts_config)
    else:
        print("\n⏭️  Skipping Azure TTS (no API key)")
    
    # Google TTS
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        google_tts_config = {
            "engine": "google",
            "credentials_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            "voice": os.getenv("TTS_GOOGLE_VOICE", "de-DE-Wavenet-C"),
            "language": "de-DE"
        }
        tts_results["google"] = test_tts_engine("google", google_tts_config)
    else:
        print("\n⏭️  Skipping Google TTS (no credentials)")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    print("\nSTT Engines:")
    for engine, result in stt_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {engine:15s} {status}")
    
    print("\nTTS Engines:")
    for engine, result in tts_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {engine:15s} {status}")
    
    total_tested = len(stt_results) + len(tts_results)
    total_passed = sum(stt_results.values()) + sum(tts_results.values())
    
    print(f"\nOverall: {total_passed}/{total_tested} engines available")
    print("="*60)


if __name__ == "__main__":
    main()
