"""
Configuration management for the AI Cold Calling Agent
"""
import os
import yaml
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file
        """
        if config_path is None:
            # Try default locations
            config_dir = Path(__file__).parent.parent.parent / "config"
            config_path = config_dir / "config.yaml"
            
            # Fall back to example config if main config doesn't exist
            if not config_path.exists():
                config_path = config_dir / "config.example.yaml"
        
        self.config_path = Path(config_path)
        self.config = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if not self.config_path.exists():
                logger.warning(f"Config file not found: {self.config_path}")
                self._create_default_config()
                return
            
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file) or {}
            
            # Override with environment variables
            self._apply_env_overrides()
            
            logger.info(f"Configuration loaded from: {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration"""
        self.config = {
            "database": {
                "type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "username": "aiagent",
                "password": "password",
                "database": "cold_calling_agent"
            },
            "speech_recognition": {
                "engine": "whisper",
                "model_size": "base",
                "language": "de",
                "device": "cpu"
            },
            "text_to_speech": {
                "engine": "coqui",
                "model_name": "tts_models/de/thorsten/tacotron2-DDC",
                "device": "cpu"
            },
            "conversation": {
                "max_turns": 50,
                "timeout_seconds": 30,
                "default_language": "de"
            },
            "emotion_recognition": {
                "enabled": True,
                "confidence_threshold": 0.7
            },
            "training": {
                "enabled": True,
                "auto_train_after_calls": 5
            },
            "logging": {
                "level": "INFO",
                "file_path": "logs/aiagent.log"
            }
        }
        logger.info("Using default configuration")
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides"""
        env_mappings = {
            # Database
            "DATABASE_HOST": ("database", "host"),
            "DATABASE_PORT": ("database", "port"),
            "DATABASE_USER": ("database", "username"),
            "DATABASE_PASSWORD": ("database", "password"),
            "DATABASE_NAME": ("database", "database"),
            
            # STT - General
            "STT_ENGINE": ("speech_recognition", "engine"),
            "STT_LANGUAGE": ("speech_recognition", "language"),
            
            # STT - Whisper
            "STT_WHISPER_MODEL_SIZE": ("speech_recognition", "model_size"),
            "STT_WHISPER_DEVICE": ("speech_recognition", "device"),
            
            # STT - Deepgram
            "DEEPGRAM_API_KEY": ("speech_recognition", "api_key"),
            "STT_DEEPGRAM_MODEL": ("speech_recognition", "model"),
            
            # STT - Azure
            "AZURE_SPEECH_KEY": ("speech_recognition", "api_key"),
            "AZURE_SPEECH_REGION": ("speech_recognition", "region"),
            
            # STT - Google
            "GOOGLE_APPLICATION_CREDENTIALS": ("speech_recognition", "credentials_path"),
            "STT_GOOGLE_MODEL": ("speech_recognition", "model"),
            
            # TTS - General
            "TTS_ENGINE": ("text_to_speech", "engine"),
            "TTS_LANGUAGE": ("text_to_speech", "language"),
            
            # TTS - Coqui
            "TTS_COQUI_MODEL": ("text_to_speech", "model_name"),
            "TTS_COQUI_VOCODER": ("text_to_speech", "vocoder"),
            "TTS_COQUI_DEVICE": ("text_to_speech", "device"),
            "TTS_COQUI_SPEAKER": ("text_to_speech", "speaker"),
            
            # TTS - Mimic3
            "TTS_MIMIC3_VOICE": ("text_to_speech", "voice"),
            "TTS_MIMIC3_URL": ("text_to_speech", "url"),
            
            # TTS - ElevenLabs
            "ELEVENLABS_API_KEY": ("text_to_speech", "api_key"),
            "TTS_ELEVENLABS_VOICE_ID": ("text_to_speech", "voice_id"),
            "TTS_ELEVENLABS_MODEL": ("text_to_speech", "model"),
            "TTS_ELEVENLABS_STABILITY": ("text_to_speech", "stability"),
            "TTS_ELEVENLABS_SIMILARITY_BOOST": ("text_to_speech", "similarity_boost"),
            
            # TTS - Azure (shares api_key and region with STT)
            "TTS_AZURE_VOICE": ("text_to_speech", "voice"),
            "TTS_AZURE_RATE": ("text_to_speech", "rate"),
            "TTS_AZURE_PITCH": ("text_to_speech", "pitch"),
            
            # TTS - Google (shares credentials_path with STT)
            "TTS_GOOGLE_VOICE": ("text_to_speech", "voice"),
            "TTS_GOOGLE_SPEAKING_RATE": ("text_to_speech", "speaking_rate"),
            "TTS_GOOGLE_PITCH": ("text_to_speech", "pitch"),
            
            # Other
            "LOG_LEVEL": ("logging", "level"),
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                if section not in self.config:
                    self.config[section] = {}
                
                # Convert port to integer
                if key == "port":
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                
                # Convert float values
                if key in ["stability", "similarity_boost", "speaking_rate", "pitch"]:
                    try:
                        value = float(value)
                    except ValueError:
                        continue
                
                self.config[section][key] = value
                logger.debug(f"Override from env: {env_var} = {value}")
    
    def get(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            section: Configuration section
            key: Configuration key (optional)
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        if key is None:
            return self.config.get(section, default)
        
        section_config = self.config.get(section, {})
        return section_config.get(key, default)
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        db_config = self.config.get("database", {})
        db_type = db_config.get("type", "postgresql")
        host = db_config.get("host", "localhost")
        port = db_config.get("port", 5432)
        username = db_config.get("username", "aiagent")
        password = db_config.get("password", "password")
        database = db_config.get("database", "cold_calling_agent")
        
        if db_type == "postgresql":
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
        elif db_type == "mysql":
            return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.config.get(section, {})
    
    def set(self, section: str, key: str, value: Any):
        """Set configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def save_config(self, path: Optional[str] = None):
        """Save configuration to file"""
        save_path = Path(path) if path else self.config_path
        
        try:
            # Create directory if it doesn't exist
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"Configuration saved to: {save_path}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise
    
    def validate_config(self) -> Dict[str, List[str]]:
        """
        Validate configuration
        
        Returns:
            Dictionary with validation errors by section
        """
        errors = {}
        
        # Validate database config
        db_errors = []
        db_config = self.config.get("database", {})
        
        required_db_fields = ["type", "host", "port", "username", "password", "database"]
        for field in required_db_fields:
            if not db_config.get(field):
                db_errors.append(f"Missing required field: {field}")
        
        if db_config.get("type") not in ["postgresql", "mysql"]:
            db_errors.append("Invalid database type. Must be 'postgresql' or 'mysql'")
        
        if db_errors:
            errors["database"] = db_errors
        
        # Validate speech recognition config
        stt_errors = []
        stt_config = self.config.get("speech_recognition", {})
        
        if stt_config.get("engine") not in ["whisper"]:
            stt_errors.append("Invalid STT engine. Must be 'whisper'")
        
        if stt_config.get("model_size") not in ["tiny", "base", "small", "medium", "large"]:
            stt_errors.append("Invalid Whisper model size")
        
        if stt_errors:
            errors["speech_recognition"] = stt_errors
        
        # Validate TTS config
        tts_errors = []
        tts_config = self.config.get("text_to_speech", {})
        
        if tts_config.get("engine") not in ["coqui", "mimic3"]:
            tts_errors.append("Invalid TTS engine. Must be 'coqui' or 'mimic3'")
        
        if tts_errors:
            errors["text_to_speech"] = tts_errors
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        errors = self.validate_config()
        return len(errors) == 0
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"ConfigManager(config_path={self.config_path})"


def create_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """Factory function to create configuration manager"""
    return ConfigManager(config_path)