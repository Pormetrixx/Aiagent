# AI Cold Calling Agent - Setup and Usage Guide

## Quick Start

1. **Setup the environment:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure voice engines via .env file:**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit and add your API keys
   nano .env
   ```
   
   **Important:** Die `.env`-Datei ist alles, was Sie brauchen! Die `config.yaml` ist optional.

3. **Set up your database:**
   - Install PostgreSQL or MySQL
   - Create a database named `cold_calling_agent`
   - Update database credentials in `.env`

4. **Test voice engines:**
   ```bash
   python3 tests/test_voice_engines.py
   ```

5. **Start the agent:**
   ```bash
   python3 run.py start
   ```

## Detailed Installation

### Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv

# For audio processing
sudo apt install -y ffmpeg portaudio19-dev

# For PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# For MySQL (alternative)
sudo apt install -y mysql-server
```

### Python Environment Setup

```bash
# Clone repository
git clone https://github.com/Pormetrixx/Aiagent.git
cd Aiagent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

### Configuration Methods

Das System unterstützt zwei Konfigurationsmethoden:

#### Methode 1: Nur .env-Datei (Empfohlen)

**Sie benötigen nur die `.env`-Datei!** Das ist der einfachste und empfohlene Weg:

```bash
# .env-Datei erstellen
cp .env.example .env

# Bearbeiten und API-Schlüssel hinzufügen
nano .env
```

Das System verwendet Standardwerte für alle nicht gesetzten Optionen. Die `config.yaml`-Datei ist **optional** und wird nur für erweiterte Konfigurationen benötigt.

#### Methode 2: .env + config.yaml (Optional, für erweiterte Setups)

Wenn Sie zusätzliche Konfigurationsoptionen benötigen, die nicht über Umgebungsvariablen verfügbar sind:

```bash
# Optional: config.yaml erstellen
cp config/config.example.yaml config/config.yaml

# Erweiterte Einstellungen bearbeiten
nano config/config.yaml
```

**Wichtig:** Umgebungsvariablen aus `.env` überschreiben immer die Werte in `config.yaml`.

### Voice Engine Configuration via .env

The easiest way to configure voice engines is via the `.env` file:

```bash
# Copy the example
cp .env.example .env

# Edit with your settings
nano .env
```

### Speech-to-Text (STT) Setup

#### Option 1: Whisper (Local, Free)

**Pros**: Free, runs locally, no API limits, good quality
**Cons**: Requires CPU/GPU resources, slower than cloud APIs

```bash
# In .env file:
STT_ENGINE=whisper
STT_WHISPER_MODEL_SIZE=base    # tiny, base, small, medium, large
STT_WHISPER_DEVICE=cpu         # Use 'cuda' if you have GPU
STT_LANGUAGE=de
```

**GPU Acceleration (Optional):**
```bash
# Install CUDA toolkit if you have NVIDIA GPU
# Then install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Option 2: Deepgram (Cloud API, Excellent for German)

**Pros**: Fast, excellent quality for German, Nova-2 model
**Cons**: Requires API key, usage-based pricing

1. Sign up at https://console.deepgram.com/
2. Create an API key
3. Add to `.env`:

```bash
STT_ENGINE=deepgram
DEEPGRAM_API_KEY=your_api_key_here
STT_DEEPGRAM_MODEL=nova-2
STT_LANGUAGE=de
```

**Pricing**: $200 free credits, then $0.0043/minute

#### Option 3: Azure Speech Services (Enterprise)

**Pros**: Reliable, enterprise-grade, good German support
**Cons**: Requires Azure account, usage-based pricing

1. Create Azure account: https://portal.azure.com/
2. Create "Speech Services" resource
3. Get API key and region
4. Add to `.env`:

```bash
STT_ENGINE=azure
AZURE_SPEECH_KEY=your_azure_key_here
AZURE_SPEECH_REGION=westeurope
STT_LANGUAGE=de
```

**Pricing**: 5 hours/month free, then from €0.84/hour

#### Option 4: Google Cloud Speech-to-Text

**Pros**: High accuracy, low latency, good quality
**Cons**: Requires GCP account, complex setup

1. Create GCP account: https://console.cloud.google.com/
2. Enable "Cloud Speech-to-Text API"
3. Create service account and download JSON credentials
4. Add to `.env`:

```bash
STT_ENGINE=google
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
STT_GOOGLE_MODEL=latest_long
STT_LANGUAGE=de
```

**Pricing**: $300 free credits for new accounts, then $0.006/15 seconds

### Text-to-Speech (TTS) Setup

#### Option 1: Coqui TTS (Local, Free)

**Pros**: Free, runs locally, customizable voices
**Cons**: Slower synthesis, requires CPU/GPU

```bash
# In .env file:
TTS_ENGINE=coqui
TTS_COQUI_MODEL=tts_models/de/thorsten/tacotron2-DDC
TTS_COQUI_VOCODER=vocoder_models/de/thorsten/hifigan
TTS_COQUI_DEVICE=cpu
TTS_LANGUAGE=de
```

**Available German voices:**
- `tts_models/de/thorsten/tacotron2-DDC` (male, professional)
- `tts_models/de/thorsten/vits` (male, faster)

#### Option 2: Mimic3 (Local Server, Free)

**Pros**: Free, fast, local server
**Cons**: Requires running Mimic3 server

1. Install Mimic3:
```bash
# Using Docker
docker run -p 59125:59125 mycroftai/mimic3

# Or install from source
git clone https://github.com/MycroftAI/mimic3
cd mimic3
./install.sh
mimic3-server
```

2. Configure in `.env`:
```bash
TTS_ENGINE=mimic3
TTS_MIMIC3_VOICE=de_DE/thorsten_low
TTS_MIMIC3_URL=http://localhost:59125
TTS_LANGUAGE=de
```

#### Option 3: ElevenLabs (Premium Quality)

**Pros**: Extremely natural voices, best quality, voice cloning
**Cons**: Premium pricing, requires API key

1. Sign up at https://elevenlabs.io/
2. Create API key in dashboard
3. Choose or create German voice
4. Add to `.env`:

```bash
TTS_ENGINE=elevenlabs
ELEVENLABS_API_KEY=your_api_key_here
TTS_ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
TTS_ELEVENLABS_MODEL=eleven_multilingual_v2
TTS_ELEVENLABS_STABILITY=0.5
TTS_ELEVENLABS_SIMILARITY_BOOST=0.75
TTS_LANGUAGE=de
```

**Pricing**: From $5/month for 30,000 characters

**Recommended German voices:**
- Professional female voice for cold calling
- Custom voice cloning for brand consistency

#### Option 4: Azure Neural TTS (Professional)

**Pros**: Professional quality, many voices, reliable
**Cons**: Requires Azure account

```bash
TTS_ENGINE=azure
AZURE_SPEECH_KEY=your_azure_key_here
AZURE_SPEECH_REGION=westeurope
TTS_AZURE_VOICE=de-DE-KatjaNeural
TTS_AZURE_RATE=+0%
TTS_AZURE_PITCH=+0%
TTS_LANGUAGE=de
```

**Recommended German voices:**
- `de-DE-KatjaNeural` (female, friendly, professional)
- `de-DE-ConradNeural` (male, authoritative)
- `de-DE-AmalaNeural` (female, warm)

#### Option 5: Google Cloud TTS (High Quality)

**Pros**: WaveNet and Neural2 voices, high quality
**Cons**: Requires GCP account

```bash
TTS_ENGINE=google
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
TTS_GOOGLE_VOICE=de-DE-Wavenet-C
TTS_GOOGLE_SPEAKING_RATE=1.0
TTS_GOOGLE_PITCH=0.0
TTS_LANGUAGE=de
```

**Recommended German voices:**
- `de-DE-Wavenet-C` (female, natural)
- `de-DE-Neural2-B` (male, professional)
- `de-DE-Neural2-F` (female, clear)

### Database Setup

The system supports both PostgreSQL and MySQL. Update `config/config.yaml` or `.env`:

#### PostgreSQL (Recommended)

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE cold_calling_agent;
CREATE USER aiagent WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE cold_calling_agent TO aiagent;
\q
```

In `.env`:
```bash
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=aiagent
DATABASE_PASSWORD=your_password
DATABASE_NAME=cold_calling_agent
```

#### MySQL (Alternative)

```bash
# Install MySQL
sudo apt install mysql-server

# Secure installation
sudo mysql_secure_installation

# Create database
sudo mysql
CREATE DATABASE cold_calling_agent;
CREATE USER 'aiagent'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON cold_calling_agent.* TO 'aiagent'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

In `.env`:
```bash
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=aiagent
DATABASE_PASSWORD=your_password
DATABASE_NAME=cold_calling_agent
```

### Asterisk Integration

Configure Asterisk PBX for professional call management:

```yaml
asterisk:
  enabled: true
  host: "localhost"
  port: 5038
  username: "admin"
  password: "secret"
  channel_technology: "SIP"
  context: "outbound"
  caller_id: "AI Agent <1000>"
```

**Note**: See `docs/ASTERISK_SETUP.md` for detailed Asterisk configuration instructions.

## Testing Voice Engines

Before starting the agent, test your configured voice engines:

```bash
python3 tests/test_voice_engines.py
```

This will:
- Check availability of all configured engines
- Test STT with sample audio (if available)
- Test TTS and create audio samples in `recordings/test_output/`
- Show a summary of all tests

**Sample output:**
```
============================================================
AI Cold Calling Agent - Voice Engine Test Suite
============================================================

============================================================
SPEECH-TO-TEXT ENGINES
============================================================

============================================================
Testing STT Engine: WHISPER
============================================================
✅ whisper STT is available
   Type: WhisperSTT
   Language: de

============================================================
Testing STT Engine: DEEPGRAM
============================================================
✅ deepgram STT is available
   Type: DeepgramSTT
   Language: de

...

============================================================
TEST SUMMARY
============================================================

STT Engines:
  whisper         ✅ PASSED
  deepgram        ✅ PASSED

TTS Engines:
  coqui           ✅ PASSED
  elevenlabs      ✅ PASSED

Overall: 4/4 engines available
============================================================
```

## Running the System

### Command Line Interface

```bash
# Initialize configuration
python3 run.py init

# Validate configuration
python3 run.py validate

# Start the agent
python3 run.py start

# Start with custom config
python3 run.py start -c /path/to/config.yaml
```

### As a System Service

```bash
# Install as systemd service (run setup.sh as root)
sudo ./setup.sh

# Start/stop the service
sudo systemctl start aiagent
sudo systemctl stop aiagent

# View logs
sudo journalctl -u aiagent -f
```

## Troubleshooting

### Common Issues

#### 1. STT/TTS Engine Not Available

**Problem**: Test script shows "❌ Engine NOT available"

**Solutions**:

**For Whisper:**
```bash
# Check PyTorch installation
python3 -c "import torch; print(torch.__version__)"

# Check Whisper installation
python3 -c "import whisper; print(whisper.__version__)"

# Reinstall if needed
pip install --upgrade openai-whisper torch
```

**For Deepgram:**
```bash
# Verify API key is set
echo $DEEPGRAM_API_KEY

# Test API key
curl -X GET \
  https://api.deepgram.com/v1/projects \
  -H "Authorization: Token $DEEPGRAM_API_KEY"

# Check SDK installation
pip install --upgrade deepgram-sdk
```

**For Azure:**
```bash
# Verify credentials
echo $AZURE_SPEECH_KEY
echo $AZURE_SPEECH_REGION

# Check SDK installation
pip install --upgrade azure-cognitiveservices-speech

# Test connection
python3 -c "import azure.cognitiveservices.speech as speechsdk; print('OK')"
```

**For Google Cloud:**
```bash
# Verify credentials path
echo $GOOGLE_APPLICATION_CREDENTIALS
ls -la $GOOGLE_APPLICATION_CREDENTIALS

# Test credentials
gcloud auth application-default print-access-token

# Check SDK installation
pip install --upgrade google-cloud-speech google-cloud-texttospeech
```

**For ElevenLabs:**
```bash
# Verify API key
echo $ELEVENLABS_API_KEY

# Test API connection
curl -X GET https://api.elevenlabs.io/v1/voices \
  -H "xi-api-key: $ELEVENLABS_API_KEY"

# Check SDK installation
pip install --upgrade elevenlabs
```

#### 2. Poor Audio Quality

**Problem**: Synthesized speech sounds robotic or unclear

**Solutions**:

**For Coqui TTS:**
```bash
# Use better model with vocoder
TTS_COQUI_MODEL=tts_models/de/thorsten/tacotron2-DDC
TTS_COQUI_VOCODER=vocoder_models/de/thorsten/hifigan

# Increase sample rate in synthesis
# Edit code to use 22050 Hz or 48000 Hz
```

**For Cloud APIs:**
```bash
# For Azure, use Neural voices
TTS_AZURE_VOICE=de-DE-KatjaNeural

# For Google, use WaveNet or Neural2
TTS_GOOGLE_VOICE=de-DE-Neural2-F

# For ElevenLabs, adjust stability and similarity
TTS_ELEVENLABS_STABILITY=0.7
TTS_ELEVENLABS_SIMILARITY_BOOST=0.8
```

#### 3. High Latency / Slow Response

**Problem**: Long delays between speech and response

**Solutions**:

**Optimize STT:**
```bash
# Use faster model for Whisper
STT_WHISPER_MODEL_SIZE=tiny  # or base

# Use GPU acceleration
STT_WHISPER_DEVICE=cuda

# Or switch to cloud API for faster processing
STT_ENGINE=deepgram
```

**Optimize TTS:**
```bash
# Use faster local model
TTS_ENGINE=mimic3

# Or use fast cloud API
TTS_ENGINE=azure
```

**Network optimization:**
```bash
# Check network latency to cloud APIs
ping api.deepgram.com
ping speech.googleapis.com

# Use CDN regions closer to your location
AZURE_SPEECH_REGION=westeurope  # Change to nearest region
```

#### 4. API Rate Limits / Quota Exceeded

**Problem**: "429 Too Many Requests" or quota errors

**Solutions**:

**Deepgram:**
```bash
# Check usage at https://console.deepgram.com/
# Upgrade plan or implement rate limiting
# Fallback to Whisper for overflow

# In code, implement retry logic with exponential backoff
```

**Azure:**
```bash
# Check quotas in Azure Portal
# Increase quota or upgrade tier
# Monitor usage with Azure Cost Management
```

**Google Cloud:**
```bash
# Check quota at https://console.cloud.google.com/iam-admin/quotas
# Request quota increase
# Enable billing for higher limits
```

**ElevenLabs:**
```bash
# Check character usage in dashboard
# Upgrade subscription plan
# Implement character counting before synthesis
```

#### 5. Database Connection Failed

**Problem**: Cannot connect to database

**Solutions**:

**Check PostgreSQL:**
```bash
# Verify PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -h localhost -U aiagent -d cold_calling_agent

# Check credentials in .env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=aiagent
DATABASE_PASSWORD=your_password
DATABASE_NAME=cold_calling_agent
```

**Fix common issues:**
```bash
# Reset password
sudo -u postgres psql
ALTER USER aiagent WITH PASSWORD 'new_password';

# Grant permissions
GRANT ALL PRIVILEGES ON DATABASE cold_calling_agent TO aiagent;

# Edit pg_hba.conf to allow local connections
sudo nano /etc/postgresql/*/main/pg_hba.conf
# Add line: local all aiagent md5
sudo systemctl restart postgresql
```

#### 6. Module Import Errors

**Problem**: "ModuleNotFoundError" when running scripts

**Solutions**:

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Check for missing dependencies
pip list

# Install specific missing module
pip install module-name

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

#### 7. Audio Device Not Found

**Problem**: "Error opening audio device" or similar

**Solutions**:

```bash
# Check audio devices
python3 -c "import pyaudio; p = pyaudio.PyAudio(); print(p.get_default_input_device_info())"

# Install audio libraries
sudo apt install portaudio19-dev python3-pyaudio

# Reinstall PyAudio
pip uninstall pyaudio
pip install pyaudio

# For server without audio device, use file-based I/O
# Configure in config.yaml to use file input/output instead of live audio
```

#### 8. Memory Issues with Large Models

**Problem**: "Out of memory" errors with Whisper or Coqui

**Solutions**:

```bash
# Use smaller Whisper model
STT_WHISPER_MODEL_SIZE=tiny  # or base instead of large

# Monitor memory usage
free -h
htop

# Increase swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Or switch to cloud API to offload processing
STT_ENGINE=deepgram
TTS_ENGINE=azure
```

#### 9. SSL/TLS Certificate Errors

**Problem**: SSL verification errors with cloud APIs

**Solutions**:

```bash
# Update CA certificates
sudo apt update
sudo apt install --reinstall ca-certificates

# Update Python certifi
pip install --upgrade certifi

# Check system time (important for SSL)
date
sudo ntpdate pool.ntp.org

# If behind corporate proxy, set environment variables
export HTTPS_PROXY=http://proxy.example.com:8080
export HTTP_PROXY=http://proxy.example.com:8080
```

#### 10. Configuration Not Loading

**Problem**: Changes to .env or config.yaml not taking effect

**Solutions**:

```bash
# Verify .env file is in the correct location
ls -la .env

# Check file permissions
chmod 600 .env

# Restart the application
python3 run.py stop
python3 run.py start

# Clear any cached config
rm -rf __pycache__
rm -f config/*.pyc

# Validate configuration
python3 run.py validate

# Check environment variables are loaded
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('STT_ENGINE'))"
```

### Performance Tuning

#### For Maximum Speed:
```bash
STT_ENGINE=deepgram
STT_DEEPGRAM_MODEL=nova-2
TTS_ENGINE=azure
TTS_AZURE_VOICE=de-DE-KatjaNeural
```

#### For Best Quality:
```bash
STT_ENGINE=google
STT_GOOGLE_MODEL=latest_long
TTS_ENGINE=elevenlabs
TTS_ELEVENLABS_MODEL=eleven_multilingual_v2
```

#### For Cost Efficiency:
```bash
STT_ENGINE=whisper
STT_WHISPER_MODEL_SIZE=base
STT_WHISPER_DEVICE=cuda  # If available
TTS_ENGINE=coqui
TTS_COQUI_DEVICE=cuda  # If available
```

#### For Privacy (On-Premise Only):
```bash
STT_ENGINE=whisper
TTS_ENGINE=coqui
# No cloud APIs used, all processing local
```

### Logs and Debugging

**Enable debug logging:**
```bash
# In .env
LOG_LEVEL=DEBUG

# View logs in real-time
tail -f logs/aiagent.log

# Filter for errors
grep ERROR logs/aiagent.log

# Check specific engine logs
grep "Deepgram\|Azure\|Google\|ElevenLabs" logs/aiagent.log
```

**Test individual components:**
```bash
# Test STT only
python3 -c "
from src.speech import create_stt_engine
stt = create_stt_engine({'engine': 'whisper', 'model_size': 'base', 'language': 'de'})
print('STT available:', stt.is_available())
"

# Test TTS only
python3 -c "
from src.speech import create_tts_engine
tts = create_tts_engine({'engine': 'coqui', 'model_name': 'tts_models/de/thorsten/tacotron2-DDC', 'device': 'cpu'})
print('TTS available:', tts.is_available())
"
```

### Getting Help

If you encounter issues not covered here:

1. Check the logs: `logs/aiagent.log`
2. Run the test suite: `python3 tests/test_voice_engines.py`
3. Verify your configuration: `python3 run.py validate`
4. Check GitHub Issues: https://github.com/Pormetrixx/Aiagent/issues
5. Review the documentation in `docs/` directory

## Architecture Overview

### Core Components

1. **Speech Processing** (`src/speech/`)
   - **Base Classes** (`base.py`): Abstract interfaces for STT and TTS engines
   - **STT Engines**:
     - `WhisperSTT`: Local OpenAI Whisper
     - `DeepgramSTT`: Cloud-based Deepgram API
     - `AzureSTT`: Azure Speech Services
     - `GoogleSTT`: Google Cloud Speech-to-Text
   - **TTS Engines**:
     - `CoquiTTS`: Local Coqui TTS
     - `Mimic3TTS`: Local Mimic3 server
     - `ElevenLabsTTS`: Cloud-based ElevenLabs API
     - `AzureTTS`: Azure Neural TTS
     - `GoogleTTS`: Google Cloud Text-to-Speech
   - **Factory Functions**: Dynamic engine creation based on configuration

2. **Conversation Management** (`src/conversation/`)
   - State machine for call flow management
   - Emotion recognition and adaptation
   - Response generation

3. **Database** (`src/database/`)
   - Conversation storage
   - FAQ and knowledge base
   - Training data collection

4. **Configuration** (`src/config.py`)
   - Environment variable support (.env)
   - YAML configuration file support
   - Dynamic engine selection

5. **Training System** (`src/training/`)
   - Continuous improvement
   - Performance analytics
   - Automated training cycles

### Database Schema

The system creates the following tables:
- `conversations` - Call records
- `conversation_turns` - Individual exchanges
- `faq_entries` - Knowledge base
- `conversation_scripts` - Response templates
- `training_data` - Learning data
- `customers` - Customer information
- `call_metrics` - Performance data

### Conversation Flow

1. **Opening** - Initial greeting and introduction
2. **Questioning** - Needs assessment
3. **Presenting** - Value proposition
4. **Objection Handling** - Address concerns
5. **Closing** - Appointment scheduling
6. **Follow-up** - Next steps

## Features

### Emotion Recognition

The system detects customer emotions through:
- Text analysis (keyword-based and ML)
- Audio analysis (voice features)
- Facial expression analysis (if video available)

### Continuous Learning

- Analyzes conversation outcomes
- Generates training data automatically
- Improves response quality over time
- Tracks performance metrics

### Scalability

- Supports multiple concurrent calls
- Database-backed for reliability
- Configurable resource usage
- Monitoring and logging

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check database credentials in config
   - Ensure database server is running
   - Verify network connectivity

2. **Speech Recognition Not Working**
   - Install required audio libraries
   - Check microphone permissions
   - Verify Whisper model download

3. **TTS Not Working**
   - Check TTS engine installation
   - Verify model paths
   - Test audio output devices

### Logs

System logs are stored in `logs/aiagent.log`. Check this file for detailed error information.

### Performance Tuning

- Use GPU for better Whisper performance
- Adjust pool sizes for database connections
- Monitor memory usage with larger models

## Development

### Adding New Features

1. Create new modules in appropriate directories
2. Update `__init__.py` files for imports
3. Add configuration options in `config.example.yaml`
4. Write tests for new functionality

### Database Migrations

When modifying database schema:
1. Update models in `src/database/models.py`
2. Create migration scripts in `sql/`
3. Test with development database first

### Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Include docstrings for public methods
4. Test changes thoroughly

## Support

For issues and questions:
1. Check logs for error details
2. Validate configuration with `python3 run.py validate`
3. Review this documentation
4. Check system requirements