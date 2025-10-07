# Quick Reference Guide - Voice APIs

## For Developers

### Adding a New Voice Engine

Follow these steps to add a new STT or TTS engine:

#### 1. Create Engine Class

**For STT Engine:**
```python
# src/speech/stt_newengine.py
from .base import BaseSTTEngine
from typing import Dict, Any, Union
import numpy as np

class NewEngineSTT(BaseSTTEngine):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Initialize your engine
        self.api_key = config.get("api_key")
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        # Setup API client
        pass
    
    def transcribe_file(self, audio_file_path: str, **kwargs) -> Dict[str, Any]:
        # Implement file transcription
        return {
            "text": "transcribed text",
            "language": self.language,
            "confidence": 0.95,
            "segments": []
        }
    
    def transcribe_audio_data(self, audio_data: Union[np.ndarray, bytes], 
                             sample_rate: int = 16000, **kwargs) -> Dict[str, Any]:
        # Implement data transcription
        pass
    
    def is_available(self) -> bool:
        return self.client is not None
```

**For TTS Engine:**
```python
# src/speech/tts_newengine.py
from .base import BaseTTSEngine
from typing import Dict, Any, Union, Optional

class NewEngineTTS(BaseTTSEngine):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Initialize your engine
        self.api_key = config.get("api_key")
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        # Setup API client
        pass
    
    def synthesize(self, text: str, output_path: Optional[str] = None, 
                   **kwargs) -> Union[str, bytes]:
        # Implement synthesis
        audio_data = b"..." # Your synthesis code
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            return output_path
        return audio_data
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def get_voices(self) -> list:
        # Optional: return available voices
        return []
```

#### 2. Update Factory Function

**For STT:**
```python
# In src/speech/stt.py, update create_stt_engine():

def create_stt_engine(config: Dict[str, Any]):
    engine_type = config.get("engine", "whisper").lower()
    
    # ... existing engines ...
    
    elif engine_type == "newengine":
        from .stt_newengine import NewEngineSTT
        return NewEngineSTT(config)
    
    else:
        raise ValueError(f"Unsupported STT engine: {engine_type}")
```

**For TTS:**
```python
# In src/speech/tts.py, update create_tts_engine():

def create_tts_engine(config: Dict[str, Any]) -> TTSEngine:
    engine_type = config.get("engine", "coqui").lower()
    
    # ... existing engines ...
    
    elif engine_type == "newengine":
        engine_config = {
            "api_key": config.get("api_key"),
            "voice": config.get("voice"),
            "language": config.get("language", "de")
        }
    
    # ... rest of function ...
```

#### 3. Update Configuration

**Add to .env.example:**
```bash
# ============================================================================
# NewEngine Configuration
# ============================================================================
# Get your API key from: https://newengine.example.com/
NEWENGINE_API_KEY=your_api_key_here
STT_NEWENGINE_VOICE=german_voice_id
TTS_NEWENGINE_VOICE=german_voice_id
```

**Add to src/config.py:**
```python
def _apply_env_overrides(self):
    env_mappings = {
        # ... existing mappings ...
        
        # NewEngine
        "NEWENGINE_API_KEY": ("speech_recognition", "api_key"),
        "STT_NEWENGINE_VOICE": ("speech_recognition", "voice"),
        "TTS_NEWENGINE_VOICE": ("text_to_speech", "voice"),
    }
    # ... rest of function ...
```

#### 4. Update Dependencies

**Add to requirements.txt:**
```
# NewEngine SDK
newengine-sdk>=1.0.0
```

#### 5. Update Documentation

**Add to README.md:**
```markdown
### NewEngine (Cloud API)
- **NewEngine STT** - Description
- **NewEngine TTS** - Description
```

**Add to SETUP.md:**
```markdown
#### Option X: NewEngine

**Pros**: List advantages
**Cons**: List disadvantages

1. Sign up at https://newengine.example.com/
2. Create API key
3. Add to `.env`:

```bash
STT_ENGINE=newengine
NEWENGINE_API_KEY=your_api_key_here
```
```

#### 6. Update Tests

**Add to tests/test_voice_engines.py:**
```python
# NewEngine
if os.getenv("NEWENGINE_API_KEY"):
    newengine_config = {
        "engine": "newengine",
        "api_key": os.getenv("NEWENGINE_API_KEY"),
        "language": "de"
    }
    stt_results["newengine"] = test_stt_engine("newengine", newengine_config)
else:
    print("\n⏭️  Skipping NewEngine (no API key)")
```

#### 7. Test Your Engine

```bash
# Test syntax
python3 -m py_compile src/speech/stt_newengine.py

# Run full test suite
python3 tests/test_voice_engines.py

# Test in isolation
python3 -c "
from src.speech.stt_newengine import NewEngineSTT
engine = NewEngineSTT({'api_key': 'test'})
print('Available:', engine.is_available())
"
```

## Configuration Quick Reference

### Environment Variables by Engine

**Whisper (STT):**
```bash
STT_ENGINE=whisper
STT_WHISPER_MODEL_SIZE=base
STT_WHISPER_DEVICE=cpu
```

**Deepgram (STT):**
```bash
STT_ENGINE=deepgram
DEEPGRAM_API_KEY=xxx
STT_DEEPGRAM_MODEL=nova-2
```

**Azure (STT/TTS):**
```bash
STT_ENGINE=azure / TTS_ENGINE=azure
AZURE_SPEECH_KEY=xxx
AZURE_SPEECH_REGION=westeurope
TTS_AZURE_VOICE=de-DE-KatjaNeural
```

**Google (STT/TTS):**
```bash
STT_ENGINE=google / TTS_ENGINE=google
GOOGLE_APPLICATION_CREDENTIALS=/path/to/creds.json
TTS_GOOGLE_VOICE=de-DE-Wavenet-C
```

**ElevenLabs (TTS):**
```bash
TTS_ENGINE=elevenlabs
ELEVENLABS_API_KEY=xxx
TTS_ELEVENLABS_VOICE_ID=xxx
```

**Coqui (TTS):**
```bash
TTS_ENGINE=coqui
TTS_COQUI_MODEL=tts_models/de/thorsten/tacotron2-DDC
TTS_COQUI_DEVICE=cpu
```

**Mimic3 (TTS):**
```bash
TTS_ENGINE=mimic3
TTS_MIMIC3_VOICE=de_DE/thorsten_low
TTS_MIMIC3_URL=http://localhost:59125
```

## Common Code Patterns

### Initialize Engine from Config

```python
from src.config import ConfigManager

config = ConfigManager()
stt_config = config.get_section("speech_recognition")
tts_config = config.get_section("text_to_speech")

stt = create_stt_engine(stt_config)
tts = create_tts_engine(tts_config)
```

### Initialize Engine Directly

```python
from src.speech import create_stt_engine, create_tts_engine

# Manual config
stt = create_stt_engine({
    "engine": "deepgram",
    "api_key": "your_key",
    "model": "nova-2",
    "language": "de"
})

tts = create_tts_engine({
    "engine": "elevenlabs",
    "api_key": "your_key",
    "voice_id": "voice_id",
    "model": "eleven_multilingual_v2"
})
```

### Use Specific Engine

```python
from src.speech.stt_deepgram import DeepgramSTT
from src.speech.tts_elevenlabs import ElevenLabsTTS

# Direct instantiation
stt = DeepgramSTT({"api_key": "xxx", "model": "nova-2", "language": "de"})
tts = ElevenLabsTTS({"api_key": "xxx", "voice_id": "xxx"})
```

### Check Availability

```python
if not stt.is_available():
    print("STT engine not available")
    # Fallback logic
    
if not tts.is_available():
    print("TTS engine not available")
    # Fallback logic
```

### Transcribe Audio

```python
# From file
result = stt.transcribe_file("audio.wav")
print(result["text"])
print(f"Confidence: {result['confidence']:.2%}")

# From numpy array
import numpy as np
audio_data = np.array([...])  # Your audio data
result = stt.transcribe_audio_data(audio_data, sample_rate=16000)
```

### Synthesize Speech

```python
# To file
output_path = "output.wav"
tts.synthesize("Guten Tag!", output_path)

# To memory
audio_bytes = tts.synthesize("Guten Tag!")

# With options
tts.synthesize(
    "Guten Tag!",
    output_path,
    stability=0.7,  # ElevenLabs
    speaking_rate=1.1  # Google
)
```

### Get Engine Info

```python
info = stt.get_engine_info()
print(f"Engine: {info['type']}")
print(f"Language: {info['language']}")
print(f"Available: {info['available']}")

# Get available voices
voices = tts.get_voices()
for voice in voices:
    print(voice)
```

## Debugging Tips

### Enable Debug Logging

```bash
# In .env
LOG_LEVEL=DEBUG
```

### Test Individual Components

```bash
# Test STT only
python3 -c "
from src.speech import create_stt_engine
config = {'engine': 'whisper', 'model_size': 'base', 'language': 'de'}
stt = create_stt_engine(config)
print('Available:', stt.is_available())
"

# Test TTS only
python3 -c "
from src.speech import create_tts_engine
config = {'engine': 'coqui', 'model_name': 'tts_models/de/thorsten/tacotron2-DDC'}
tts = create_tts_engine(config)
print('Available:', tts.is_available())
"
```

### Check API Connectivity

```bash
# Deepgram
curl -X GET https://api.deepgram.com/v1/projects \
  -H "Authorization: Token $DEEPGRAM_API_KEY"

# ElevenLabs
curl -X GET https://api.elevenlabs.io/v1/voices \
  -H "xi-api-key: $ELEVENLABS_API_KEY"

# Azure
curl -X GET "https://${AZURE_SPEECH_REGION}.api.cognitive.microsoft.com/sts/v1.0/issuetoken" \
  -H "Ocp-Apim-Subscription-Key: $AZURE_SPEECH_KEY"
```

### Verify Environment Variables

```bash
# Check if variables are set
env | grep STT
env | grep TTS
env | grep API_KEY

# Load and check in Python
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('STT Engine:', os.getenv('STT_ENGINE'))
print('TTS Engine:', os.getenv('TTS_ENGINE'))
"
```

## Performance Benchmarks

Approximate latency for German speech (1 minute audio):

**STT Engines:**
- Whisper (CPU): 30-60 seconds
- Whisper (GPU): 5-10 seconds
- Deepgram: 2-5 seconds
- Azure: 3-7 seconds
- Google: 3-6 seconds

**TTS Engines:**
- Coqui (CPU): 10-20 seconds
- Coqui (GPU): 2-5 seconds
- Mimic3: 5-10 seconds
- ElevenLabs: 2-4 seconds
- Azure: 1-3 seconds
- Google: 2-4 seconds

## Cost Estimates (per 1000 minutes of audio)

**STT:**
- Whisper: Free
- Deepgram: ~$4.30
- Azure: ~$16.80
- Google: ~$24.00

**TTS:**
- Coqui: Free
- Mimic3: Free
- ElevenLabs: Variable (character-based)
- Azure: ~$16.80
- Google: ~$16.00

*Note: Prices approximate and may vary. Check provider websites for current pricing.*
