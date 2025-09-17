# AI Cold Calling Agent - Setup and Usage Guide

## Quick Start

1. **Setup the environment:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure the system:**
   ```bash
   # Edit the configuration file
   nano config/config.yaml
   ```

3. **Set up your database:**
   - Install PostgreSQL or MySQL
   - Create a database named `cold_calling_agent`
   - Update database credentials in `config/config.yaml`

4. **Start the agent:**
   ```bash
   python3 run.py start
   ```

## Configuration

### Database Setup

The system supports both PostgreSQL and MySQL. Update `config/config.yaml`:

```yaml
database:
  type: "postgresql"  # or "mysql"
  host: "localhost"
  port: 5432          # 3306 for MySQL
  username: "your_username"
  password: "your_password"
  database: "cold_calling_agent"
```

### Speech Recognition (Whisper)

Configure the Whisper model settings:

```yaml
speech_recognition:
  engine: "whisper"
  model_size: "base"  # tiny, base, small, medium, large
  language: "de"      # German
  device: "cpu"       # or "cuda" if you have GPU
```

### Text-to-Speech

Choose between Coqui TTS or Mimic3:

```yaml
text_to_speech:
  engine: "coqui"     # or "mimic3"
  model_name: "tts_models/de/thorsten/tacotron2-DDC"
  device: "cpu"
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

## Architecture Overview

### Core Components

1. **Speech Processing** (`src/speech/`)
   - STT: OpenAI Whisper for speech recognition
   - TTS: Coqui TTS or Mimic3 for speech synthesis

2. **Conversation Management** (`src/conversation/`)
   - State machine for call flow management
   - Emotion recognition and adaptation
   - Response generation

3. **Database** (`src/database/`)
   - Conversation storage
   - FAQ and knowledge base
   - Training data collection

4. **Training System** (`src/training/`)
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