# AI Cold Calling Agent - API Documentation

## Overview

The AI Cold Calling Agent provides a comprehensive API for managing automated cold calling campaigns with speech processing, emotion recognition, and continuous learning capabilities.

## Core Components

### 1. Main Application (`AICallingAgent`)

The main application class that orchestrates all components.

```python
from src.main import AICallingAgent

# Create and initialize agent
agent = AICallingAgent(config_path="config/config.yaml")
await agent.initialize()
await agent.start()
```

#### Methods

- `start_call(customer_phone: str, customer_name: str = None) -> str`: Start a new call
- `process_audio_input(call_id: str, audio_data: bytes) -> Dict`: Process customer audio input
- `get_call_status(call_id: str) -> Dict`: Get current call status
- `get_system_status() -> Dict`: Get overall system status
- `run_training_cycle() -> Dict`: Execute a training cycle

### 2. Configuration Management (`ConfigManager`)

Handles application configuration with YAML and environment variables.

```python
from src.config import ConfigManager

config = ConfigManager("config/config.yaml")
db_url = config.get_database_url()
stt_config = config.get_section("speech_recognition")
```

#### Methods

- `get(section: str, key: str = None, default: Any = None) -> Any`: Get configuration value
- `get_section(section: str) -> Dict`: Get entire configuration section
- `validate_config() -> Dict[str, List[str]]`: Validate configuration
- `is_valid() -> bool`: Check if configuration is valid

### 3. Database Operations

#### Models (`src.database.models`)

- `Conversation`: Call records
- `ConversationTurn`: Individual exchanges
- `FAQEntry`: Knowledge base entries
- `ConversationScript`: Response templates
- `TrainingData`: Learning data
- `Customer`: Customer information

#### Repositories (`src.database.operations`)

- `ConversationRepository`: Manage conversation data
- `FAQRepository`: Handle FAQ operations
- `ScriptRepository`: Manage conversation scripts
- `TrainingRepository`: Handle training data
- `CustomerRepository`: Manage customer data

```python
from src.database import DatabaseManager, ConversationRepository

db_manager = DatabaseManager(database_url)
conv_repo = ConversationRepository(db_manager)

# Create conversation
conversation = conv_repo.create_conversation(
    call_id="call_123",
    customer_phone="+49123456789"
)
```

### 4. Speech Processing

#### Speech-to-Text (`src.speech.stt`)

```python
from src.speech import WhisperSTT

stt = WhisperSTT(model_size="base", language="de")
result = stt.transcribe_file("audio.wav")
print(result["text"])
```

#### Text-to-Speech (`src.speech.tts`)

```python
from src.speech import TTSEngine

tts = TTSEngine("coqui", model_name="tts_models/de/thorsten/tacotron2-DDC")
audio_path = tts.synthesize("Hallo, wie geht es Ihnen?", "output.wav")
```

### 5. Conversation Management

#### State Machine (`src.conversation.state_machine`)

```python
from src.conversation import ConversationStateMachine

sm = ConversationStateMachine()
sm.start_conversation("+49123456789", "Max Mustermann")

# Process customer input
result = sm.process_customer_input("Ja, ich höre zu.")
print(f"Current state: {sm.state}")
```

#### States

1. `initial` → `opening` → `introducing` → `questioning`
2. `questioning` → `presenting` → `closing` → `scheduling`
3. `*` → `handling_objections` → `presenting`
4. `*` → `ending` / `failed` / `completed`

#### Emotion Recognition (`src.conversation.emotion_recognition`)

```python
from src.conversation import EmotionRecognitionSystem

emotion_system = EmotionRecognitionSystem()
result = emotion_system.analyze_multimodal_emotion(
    text="Ich bin sehr interessiert!",
    audio_path="customer_audio.wav"
)
print(f"Emotion: {result['smoothed_emotion']['primary_emotion']}")
```

### 6. Training System (`src.training.continuous_improvement`)

```python
from src.training import ContinuousTrainer

trainer = ContinuousTrainer(training_repo, conversation_repo)

# Check if training should be triggered
if trainer.should_trigger_training():
    result = trainer.execute_training_cycle()
    print(f"Training result: {result}")
```

## Configuration

### Database Configuration

```yaml
database:
  type: "postgresql"  # or "mysql"
  host: "localhost"
  port: 5432
  username: "aiagent"
  password: "your_password"
  database: "cold_calling_agent"
```

### Speech Configuration

```yaml
speech_recognition:
  engine: "whisper"
  model_size: "base"  # tiny, base, small, medium, large
  language: "de"
  device: "cpu"

text_to_speech:
  engine: "coqui"  # or "mimic3"
  model_name: "tts_models/de/thorsten/tacotron2-DDC"
  device: "cpu"
```

### Conversation Configuration

```yaml
conversation:
  max_turns: 50
  timeout_seconds: 30
  default_language: "de"
  emotional_adaptation: true

emotion_recognition:
  enabled: true
  confidence_threshold: 0.7
  adaptation_strength: 0.3
```

## CLI Usage

```bash
# Initialize configuration
python3 run.py init

# Validate configuration
python3 run.py validate

# Start the agent
python3 run.py start

# Start with custom config
python3 run.py start -c custom_config.yaml
```

## Docker Usage

```bash
# Build and run with Docker Compose
docker-compose up -d

# Build custom image
docker build -t aiagent .
docker run -p 8080:8080 aiagent
```

## Error Handling

The system provides comprehensive error handling:

- Database connection failures
- Speech processing errors
- Configuration validation errors
- Training failures
- Network connectivity issues

All errors are logged to the configured log file and include detailed context for debugging.

## Performance Considerations

- Use GPU for Whisper models when available
- Configure appropriate database pool sizes
- Monitor memory usage with large language models
- Use appropriate TTS model sizes for your hardware
- Regular database maintenance for optimal performance

## Security

- Database credentials should be stored in environment variables
- Use strong passwords for database access
- Regularly update dependencies for security patches
- Monitor logs for unusual activity
- Implement proper network security measures