#!/usr/bin/env python3
"""
Example: Using different voice engines for cold calling
Demonstrates how to easily switch between engines via configuration
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.speech import create_stt_engine, create_tts_engine

# German cold calling sample text
SAMPLE_TEXT = """
Guten Tag, mein Name ist Max Müller von FinanzOptima. 
Ich rufe Sie an, weil wir aktuell ausgewählten Unternehmen helfen, 
ihre Investitionsstrategien zu optimieren. 
Hätten Sie kurz Zeit für ein Gespräch?
"""


def example_whisper_coqui():
    """Example: Using local free engines (Whisper + Coqui)"""
    print("\n" + "="*60)
    print("Example 1: Local Free Engines (Whisper + Coqui)")
    print("="*60)
    
    # Configure STT
    stt_config = {
        "engine": "whisper",
        "model_size": "base",
        "device": "cpu",
        "language": "de"
    }
    
    # Configure TTS
    tts_config = {
        "engine": "coqui",
        "model_name": "tts_models/de/thorsten/tacotron2-DDC",
        "device": "cpu",
        "language": "de"
    }
    
    print("\n✅ Configuration: Whisper STT + Coqui TTS (100% local, free)")
    print("   Best for: Privacy, cost efficiency, no API limits")
    print("   Performance: Good quality, moderate speed")
    
    try:
        stt = create_stt_engine(stt_config)
        tts = create_tts_engine(tts_config)
        
        print(f"   STT Status: {'Available' if stt.is_available() else 'Not Available'}")
        print(f"   TTS Status: {'Available' if tts.is_available() else 'Not Available'}")
        
        # Synthesize sample
        if tts.is_available():
            output_path = Path(__file__).parent.parent / "recordings" / "sample_local.wav"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"\n   Synthesizing sample to: {output_path}")
            tts.synthesize(SAMPLE_TEXT, str(output_path))
            print(f"   ✅ Audio created successfully!")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")


def example_deepgram_elevenlabs():
    """Example: Using premium cloud APIs (Deepgram + ElevenLabs)"""
    print("\n" + "="*60)
    print("Example 2: Premium Cloud APIs (Deepgram + ElevenLabs)")
    print("="*60)
    
    # Check if API keys are available
    if not os.getenv("DEEPGRAM_API_KEY"):
        print("   ⏭️  Skipping - DEEPGRAM_API_KEY not set")
        return
    
    if not os.getenv("ELEVENLABS_API_KEY"):
        print("   ⏭️  Skipping - ELEVENLABS_API_KEY not set")
        return
    
    # Configure STT
    stt_config = {
        "engine": "deepgram",
        "api_key": os.getenv("DEEPGRAM_API_KEY"),
        "model": "nova-2",
        "language": "de"
    }
    
    # Configure TTS
    tts_config = {
        "engine": "elevenlabs",
        "api_key": os.getenv("ELEVENLABS_API_KEY"),
        "voice_id": os.getenv("TTS_ELEVENLABS_VOICE_ID"),
        "model": "eleven_multilingual_v2",
        "language": "de"
    }
    
    print("\n✅ Configuration: Deepgram STT + ElevenLabs TTS")
    print("   Best for: Maximum quality, natural voices, fast processing")
    print("   Performance: Excellent quality, very fast")
    
    try:
        stt = create_stt_engine(stt_config)
        tts = create_tts_engine(tts_config)
        
        print(f"   STT Status: {'Available' if stt.is_available() else 'Not Available'}")
        print(f"   TTS Status: {'Available' if tts.is_available() else 'Not Available'}")
        
        # Synthesize sample
        if tts.is_available():
            output_path = Path(__file__).parent.parent / "recordings" / "sample_premium.wav"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"\n   Synthesizing sample to: {output_path}")
            tts.synthesize(SAMPLE_TEXT, str(output_path))
            print(f"   ✅ Audio created successfully!")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")


def example_azure_enterprise():
    """Example: Using Azure for enterprise deployment"""
    print("\n" + "="*60)
    print("Example 3: Azure Enterprise (Azure STT + Azure TTS)")
    print("="*60)
    
    # Check if API keys are available
    if not os.getenv("AZURE_SPEECH_KEY"):
        print("   ⏭️  Skipping - AZURE_SPEECH_KEY not set")
        return
    
    # Configure STT
    stt_config = {
        "engine": "azure",
        "api_key": os.getenv("AZURE_SPEECH_KEY"),
        "region": os.getenv("AZURE_SPEECH_REGION", "westeurope"),
        "language": "de-DE"
    }
    
    # Configure TTS
    tts_config = {
        "engine": "azure",
        "api_key": os.getenv("AZURE_SPEECH_KEY"),
        "region": os.getenv("AZURE_SPEECH_REGION", "westeurope"),
        "voice": "de-DE-KatjaNeural",
        "language": "de-DE"
    }
    
    print("\n✅ Configuration: Azure Speech Services (STT + TTS)")
    print("   Best for: Enterprise reliability, SLA guarantees, compliance")
    print("   Performance: High quality, consistent, reliable")
    
    try:
        stt = create_stt_engine(stt_config)
        tts = create_tts_engine(tts_config)
        
        print(f"   STT Status: {'Available' if stt.is_available() else 'Not Available'}")
        print(f"   TTS Status: {'Available' if tts.is_available() else 'Not Available'}")
        
        # Synthesize sample
        if tts.is_available():
            output_path = Path(__file__).parent.parent / "recordings" / "sample_azure.wav"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"\n   Synthesizing sample to: {output_path}")
            tts.synthesize(SAMPLE_TEXT, str(output_path))
            print(f"   ✅ Audio created successfully!")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")


def example_mixed_setup():
    """Example: Using best of both worlds (Cloud STT + Local TTS)"""
    print("\n" + "="*60)
    print("Example 4: Hybrid Setup (Deepgram STT + Local TTS)")
    print("="*60)
    
    # Check if API key is available
    if not os.getenv("DEEPGRAM_API_KEY"):
        print("   ℹ️  Using Whisper instead of Deepgram (no API key)")
        stt_config = {
            "engine": "whisper",
            "model_size": "base",
            "device": "cpu",
            "language": "de"
        }
    else:
        stt_config = {
            "engine": "deepgram",
            "api_key": os.getenv("DEEPGRAM_API_KEY"),
            "model": "nova-2",
            "language": "de"
        }
    
    # Configure TTS (local)
    tts_config = {
        "engine": "coqui",
        "model_name": "tts_models/de/thorsten/tacotron2-DDC",
        "device": "cpu",
        "language": "de"
    }
    
    print("\n✅ Configuration: Fast Cloud STT + Free Local TTS")
    print("   Best for: Cost-conscious deployments with good performance")
    print("   Performance: Fast recognition, free synthesis")
    
    try:
        stt = create_stt_engine(stt_config)
        tts = create_tts_engine(tts_config)
        
        print(f"   STT Status: {'Available' if stt.is_available() else 'Not Available'}")
        print(f"   TTS Status: {'Available' if tts.is_available() else 'Not Available'}")
        
        # Synthesize sample
        if tts.is_available():
            output_path = Path(__file__).parent.parent / "recordings" / "sample_hybrid.wav"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"\n   Synthesizing sample to: {output_path}")
            tts.synthesize(SAMPLE_TEXT, str(output_path))
            print(f"   ✅ Audio created successfully!")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")


def main():
    """Run all examples"""
    print("="*60)
    print("AI Cold Calling Agent - Voice Engine Examples")
    print("="*60)
    print("\nDemonstrating flexible engine configuration for different use cases")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run examples
    example_whisper_coqui()
    example_deepgram_elevenlabs()
    example_azure_enterprise()
    example_mixed_setup()
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)
    print("\n📁 Check the 'recordings' folder for generated audio samples")
    print("💡 Tip: Switch engines by changing the .env file")
    print("📖 See docs/GERMAN_CALL_SCRIPTS.md for call scripts")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
