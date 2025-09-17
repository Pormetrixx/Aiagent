"""
Integration tests for the AI Cold Calling Agent
"""
import pytest
import asyncio
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.mark.asyncio
async def test_configuration_integration():
    """Test configuration validation"""
    from src.config import ConfigManager
    
    config = ConfigManager()
    errors = config.validate_config()
    
    # Should have some validation errors with default config
    # but basic structure should be valid
    assert isinstance(errors, dict)

@pytest.mark.asyncio
async def test_state_machine_integration():
    """Test conversation state machine"""
    from src.conversation.state_machine import ConversationStateMachine
    
    sm = ConversationStateMachine()
    
    # Test initial state
    assert sm.state == "initial"
    
    # Test basic state transitions
    sm.start_call()
    assert sm.state == "opening"
    
    sm.customer_answered()
    assert sm.state == "introducing"

if __name__ == "__main__":
    pytest.main([__file__])