"""
Complete Cold Calling Agent Example
Demonstrates the fully implemented AI cold calling system with real audio processing
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def complete_cold_calling_demo():
    """Demonstrates the complete cold calling system"""
    print("🤖 AI Cold Calling Agent - Complete Implementation Demo")
    print("=" * 60)
    
    try:
        from src.main import AICallingAgent
        
        # Create agent instance
        agent = AICallingAgent()
        
        print("📞 Initializing AI calling agent...")
        await agent.initialize()
        
        print("🚀 Starting the agent...")
        await agent.start()
        
        # Get system status
        status = await agent.get_system_status()
        print(f"✅ System Status:")
        for component, available in status["components"].items():
            status_icon = "✅" if available else "❌"
            print(f"   {status_icon} {component}: {available}")
        
        print(f"\n📊 Active calls: {status['active_calls']}")
        
        # Example: Start a call
        print(f"\n📞 Starting demonstration call...")
        call_id = await agent.start_call(
            customer_phone="+49123456789",
            customer_name="Max Mustermann"
        )
        
        print(f"✅ Call started: {call_id}")
        
        # Simulate customer conversation
        print(f"\n🎤 Simulating customer conversation...")
        
        # Example customer responses (in real usage, this would come from audio input)
        customer_responses = [
            "Hallo, ja ich höre zu.",
            "Das klingt interessant. Können Sie mir mehr erzählen?",
            "Was würde das kosten?",
            "Ja, ich hätte Interesse an einem Termin."
        ]
        
        for i, response in enumerate(customer_responses):
            print(f"\n👤 Customer says: {response}")
            
            # Convert text to simulated audio (in real usage, this would be actual audio data)
            simulated_audio = response.encode('utf-8')  # Placeholder for real audio
            
            # Process customer input
            result = await agent.process_audio_input(call_id, simulated_audio)
            
            print(f"🤖 Agent responds: {result['agent_response']}")
            print(f"😊 Detected emotion: {result['emotion']}")
            print(f"🎯 Conversation state: {result['conversation_state']}")
            
            if result['should_end']:
                print(f"📞 Call ended with outcome: {result['outcome']}")
                break
        
        # Get final call status
        final_status = await agent.get_call_status(call_id)
        if final_status:
            print(f"\n📊 Final call status:")
            print(f"   Duration: {final_status['duration']:.1f} seconds")
            print(f"   Customer: {final_status['customer_name']}")
            print(f"   Phone: {final_status['customer_phone']}")
        
        # Run a training cycle
        print(f"\n🧠 Running training cycle...")
        training_result = await agent.run_training_cycle()
        print(f"📈 Training result: {training_result['status']}")
        
        if training_result.get('training_results'):
            tr = training_result['training_results']
            print(f"   Processed: {tr.get('data_processed', 0)} data points")
            print(f"   Training loss: {tr.get('training_loss', 0):.3f}")
            print(f"   Validation accuracy: {tr.get('validation_accuracy', 0):.3f}")
        
        print(f"\n🎉 Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'agent' in locals():
            print(f"\n🛑 Stopping agent...")
            await agent.stop()


async def audio_processing_demo():
    """Demonstrates the audio processing capabilities"""
    print("\n🔊 Audio Processing Demo")
    print("=" * 30)
    
    try:
        from src.speech import WhisperSTT, create_tts_engine
        
        # Test STT
        print("🎤 Testing Speech-to-Text...")
        stt = WhisperSTT(model_size="base", language="de")
        print(f"   STT available: {stt.is_available()}")
        
        # Test TTS
        print("🔊 Testing Text-to-Speech...")
        tts_config = {
            "engine": "coqui",
            "model_name": "tts_models/de/thorsten/tacotron2-DDC",
            "device": "cpu"
        }
        
        try:
            tts = create_tts_engine(tts_config)
            print(f"   TTS available: {tts.is_available()}")
        except Exception as e:
            print(f"   TTS error: {e}")
        
    except ImportError as e:
        print(f"   Missing dependency: {e}")
        print("   Install with: pip install -r requirements.txt")


async def emotion_recognition_demo():
    """Demonstrates emotion recognition capabilities"""
    print("\n😊 Emotion Recognition Demo")
    print("=" * 35)
    
    try:
        from src.conversation.emotion_recognition import TextEmotionAnalyzer
        
        analyzer = TextEmotionAnalyzer()
        
        test_phrases = [
            "Ich bin sehr interessiert an Ihrem Angebot!",
            "Das ist viel zu teuer für mich.",
            "Ich habe keine Zeit für sowas.",
            "Das klingt wirklich fantastisch!",
            "Ich bin nicht interessiert, danke."
        ]
        
        for phrase in test_phrases:
            result = analyzer.analyze_text_emotion(phrase)
            print(f"   '{phrase}'")
            print(f"   → Emotion: {result['primary_emotion']} (confidence: {result['confidence']:.2f})")
            print()
        
    except Exception as e:
        print(f"   Error: {e}")


async def database_demo():
    """Demonstrates database operations"""
    print("\n🗄️ Database Demo")
    print("=" * 20)
    
    try:
        from src.config import ConfigManager
        
        config = ConfigManager()
        print(f"   Database type: {config.get('database', 'type')}")
        print(f"   Database host: {config.get('database', 'host')}")
        print(f"   Configuration valid: {config.is_valid()}")
        
        # Show validation errors if any
        errors = config.validate_config()
        if errors:
            print(f"   Configuration issues:")
            for section, issues in errors.items():
                for issue in issues:
                    print(f"     - {section}: {issue}")
        
    except Exception as e:
        print(f"   Error: {e}")


async def main():
    """Main demo function"""
    print("🎯 AI Cold Calling Agent - Complete Implementation")
    print("=" * 55)
    print("This demo shows all implemented features of the cold calling system:")
    print("- Real audio processing with Whisper STT and TTS")
    print("- Complete conversation management with state machine")
    print("- Emotion recognition and adaptive responses")
    print("- Database integration with training data")
    print("- Continuous learning and improvement")
    print("- Phone call integration (simulated)")
    print()
    
    # Run individual component demos
    await audio_processing_demo()
    await emotion_recognition_demo()
    await database_demo()
    
    # Ask user if they want to run the full demo
    print(f"\n❓ Would you like to run the complete cold calling demo?")
    print("   (This requires proper database setup)")
    response = input("   Enter 'y' for yes, any other key to skip: ")
    
    if response.lower() == 'y':
        await complete_cold_calling_demo()
    else:
        print("   Demo skipped. See SETUP.md for configuration instructions.")
    
    print(f"\n✅ All demos completed!")


if __name__ == "__main__":
    asyncio.run(main())