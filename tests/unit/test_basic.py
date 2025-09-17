"""
Unit tests for the AI Cold Calling Agent
"""
import pytest
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_imports():
    """Test that all main modules can be imported"""
    try:
        from src.config import ConfigManager
        from src.database.models import Conversation
        from src.speech.stt import WhisperSTT
        from src.conversation.state_machine import ConversationStateMachine
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_config_manager():
    """Test basic config manager functionality"""
    from src.config import ConfigManager
    
    # Create config manager with default config
    config = ConfigManager()
    
    # Test basic getters
    assert config.get("database", "type") in ["postgresql", "mysql"]
    assert config.get("speech_recognition", "engine") == "whisper"
    assert config.get("text_to_speech", "engine") in ["coqui", "mimic3"]

def test_database_models():
    """Test database model definitions"""
    from src.database.models import Conversation, ConversationTurn, FAQEntry
    
    # Test that models have required attributes
    assert hasattr(Conversation, 'call_id')
    assert hasattr(Conversation, 'customer_phone')
    assert hasattr(ConversationTurn, 'speaker')
    assert hasattr(FAQEntry, 'question')
    assert hasattr(FAQEntry, 'answer')

if __name__ == "__main__":
    pytest.main([__file__])