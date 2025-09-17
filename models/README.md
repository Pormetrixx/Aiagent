# Models Directory

This directory contains the AI models used by the cold calling agent:

## Structure

- `whisper/` - Whisper speech recognition models
- `tts/` - Text-to-speech models (Coqui TTS)
- `emotion/` - Emotion recognition models
- `conversation/` - Conversation understanding models

## Model Downloads

Models will be automatically downloaded on first use. You can also pre-download them:

### Whisper Models
```bash
python3 -c "import whisper; whisper.load_model('base')"
```

### Coqui TTS Models
```bash
python3 -c "from TTS.api import TTS; TTS('tts_models/de/thorsten/tacotron2-DDC')"
```

## Storage Requirements

- Whisper base model: ~142 MB
- Whisper large model: ~1.5 GB
- German TTS model: ~100 MB
- Emotion models: ~50 MB

Total recommended space: 2-3 GB