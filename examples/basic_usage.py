"""
Example usage of the AI Cold Calling Agent
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def basic_usage_example():
    """Basic usage example"""
    from src.main import AICallingAgent
    
    try:
        # Create agent instance
        agent = AICallingAgent()
        
        # Initialize the agent
        await agent.initialize()
        
        # Start the agent
        await agent.start()
        
        # Example: Start a call
        call_id = await agent.start_call(
            customer_phone="+49123456789",
            customer_name="Max Mustermann"
        )
        
        print(f"Started call: {call_id}")
        
        # Get call status
        status = await agent.get_call_status(call_id)
        print(f"Call status: {status}")
        
        # Get system status
        system_status = await agent.get_system_status()
        print(f"System status: {system_status}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'agent' in locals():
            await agent.stop()


async def configuration_example():
    """Configuration example"""
    from src.config import ConfigManager
    
    # Create config manager
    config = ConfigManager()
    
    # Get database configuration
    db_config = config.get_section("database")
    print(f"Database config: {db_config}")
    
    # Get database URL
    db_url = config.get_database_url()
    print(f"Database URL: {db_url}")
    
    # Validate configuration
    errors = config.validate_config()
    if errors:
        print(f"Configuration errors: {errors}")
    else:
        print("Configuration is valid!")


async def conversation_example():
    """Conversation management example"""
    from src.conversation.state_machine import ConversationStateMachine
    from src.conversation.emotion_recognition import TextEmotionAnalyzer
    
    # Create state machine
    sm = ConversationStateMachine()
    
    # Start conversation
    sm.start_conversation("+49123456789", "Max Mustermann")
    print(f"Initial state: {sm.state}")
    
    # Process customer input
    result = sm.process_customer_input("Hallo, ja ich höre zu.")
    print(f"Transition result: {result}")
    print(f"New state: {sm.state}")
    
    # Emotion analysis example
    emotion_analyzer = TextEmotionAnalyzer()
    emotion_result = emotion_analyzer.analyze_text_emotion("Ich bin sehr interessiert!")
    print(f"Emotion analysis: {emotion_result}")


if __name__ == "__main__":
    print("=== AI Cold Calling Agent Examples ===\n")
    
    print("1. Configuration Example:")
    asyncio.run(configuration_example())
    
    print("\n2. Conversation Example:")
    asyncio.run(conversation_example())
    
    print("\n3. Basic Usage Example:")
    print("(Note: This requires proper database setup)")
    # Uncomment to run full example:
    # asyncio.run(basic_usage_example())