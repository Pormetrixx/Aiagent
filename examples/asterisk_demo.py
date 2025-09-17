"""
Asterisk Integration Example for the AI Cold Calling Agent
Demonstrates how to use the agent with a local Asterisk server
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def asterisk_integration_demo():
    """Demonstrates Asterisk telephony integration"""
    print("📞 AI Cold Calling Agent - Asterisk Integration Demo")
    print("=" * 60)
    
    try:
        from src.telephony.asterisk import AsteriskTelephonyProvider
        
        # Asterisk configuration
        asterisk_config = {
            "host": "localhost",
            "port": 5038,
            "username": "admin",
            "password": "secret",
            "channel_technology": "SIP",
            "context": "outbound",
            "extension": "s",
            "caller_id": "AI Agent <1000>"
        }
        
        print("🔧 Initializing Asterisk telephony provider...")
        provider = AsteriskTelephonyProvider(asterisk_config)
        
        # Initialize connection
        if await provider.initialize():
            print("✅ Successfully connected to Asterisk AMI")
            
            # Register event callbacks
            provider.register_call_callback("call_answered", on_call_answered)
            provider.register_call_callback("call_ended", on_call_ended)
            provider.register_call_callback("call_connected", on_call_connected)
            
            # Make a test call
            test_number = "1000"  # Internal test extension
            print(f"\n📞 Making test call to extension {test_number}...")
            
            call_result = await provider.make_call(test_number)
            
            if call_result.get("success"):
                call_id = call_result["call_id"]
                print(f"✅ Call initiated successfully, call_id: {call_id}")
                
                # Monitor call status
                print("📊 Monitoring call status...")
                for i in range(10):  # Monitor for 10 seconds
                    status = await provider.get_call_status(call_id)
                    if status:
                        print(f"   Status: {status['status']} (Duration: {i}s)")
                        
                        if status['status'] in ['ended', 'hung_up']:
                            break
                    
                    await asyncio.sleep(1)
                
                # End call if still active
                print("📞 Ending call...")
                await provider.end_call(call_id)
                
            else:
                error = call_result.get("error", "Unknown error")
                print(f"❌ Call failed: {error}")
            
            # List active calls
            active_calls = await provider.list_active_calls()
            print(f"\n📋 Active calls: {len(active_calls)}")
            
        else:
            print("❌ Failed to connect to Asterisk AMI")
            print("   Make sure Asterisk is running and AMI is configured")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Install required dependencies: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'provider' in locals():
            print("\n🧹 Cleaning up...")
            await provider.cleanup()


async def full_asterisk_agent_demo():
    """Demonstrates the full AI agent with Asterisk integration"""
    print("\n🤖 Full AI Agent with Asterisk Demo")
    print("=" * 40)
    
    try:
        from src.main import AICallingAgent
        from src.config import ConfigManager
        
        # Create a custom config with Asterisk enabled
        config_manager = ConfigManager()
        
        # Update Asterisk configuration for demo
        config_manager.set("asterisk", "enabled", True)
        config_manager.set("asterisk", "host", "localhost")
        config_manager.set("asterisk", "port", 5038)
        config_manager.set("asterisk", "username", "admin")
        config_manager.set("asterisk", "password", "secret")
        
        print("🚀 Initializing AI agent with Asterisk...")
        agent = AICallingAgent()
        
        # Override config manager
        agent.config_manager = config_manager
        
        await agent.initialize()
        await agent.start()
        
        # Get system status
        status = await agent.get_system_status()
        print(f"\n📊 System Status:")
        for component, available in status["components"].items():
            status_icon = "✅" if available else "❌"
            print(f"   {status_icon} {component}: {available}")
        
        print(f"\n📞 Telephony Status: {status['configuration']['telephony_enabled']}")
        print(f"📡 Asterisk Host: {status['configuration']['asterisk_host']}")
        
        # Try to make a call if telephony is available
        if status["components"]["telephony"]:
            print(f"\n📞 Making demonstration call via Asterisk...")
            try:
                call_id = await agent.start_call(
                    customer_phone="1000",  # Internal test extension
                    customer_name="Test Extension"
                )
                print(f"✅ Call started: {call_id}")
                
                # Wait a bit then end the call
                await asyncio.sleep(5)
                
                final_status = await agent.get_call_status(call_id)
                if final_status:
                    print(f"📊 Call duration: {final_status['duration']:.1f} seconds")
                
            except Exception as e:
                print(f"❌ Call failed: {e}")
        else:
            print("❌ Telephony not available - check Asterisk configuration")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'agent' in locals():
            print("\n🛑 Stopping agent...")
            await agent.stop()


def on_call_answered(event_data):
    """Callback for when a call is answered"""
    print(f"📞 Call answered: {event_data.get('Channel', 'Unknown')}")


def on_call_ended(event_data):
    """Callback for when a call ends"""
    cause = event_data.get('Cause', 'Unknown')
    print(f"📞 Call ended: Cause {cause}")


def on_call_connected(event_data):
    """Callback for when a call is connected/bridged"""
    print(f"🔗 Call connected: {event_data.get('Channel1', 'Unknown')} <-> {event_data.get('Channel2', 'Unknown')}")


async def asterisk_configuration_test():
    """Test Asterisk configuration and connectivity"""
    print("\n🔧 Asterisk Configuration Test")
    print("=" * 35)
    
    try:
        from src.telephony.asterisk import AsteriskAMIManager
        
        print("📡 Testing Asterisk AMI connection...")
        
        ami = AsteriskAMIManager(
            host="localhost",
            port=5038,
            username="admin",
            password="secret"
        )
        
        if await ami.connect():
            print("✅ Connected to Asterisk AMI")
            
            if await ami.login():
                print("✅ Authentication successful")
                
                # Test call origination
                print("📞 Testing call origination...")
                result = await ami.originate_call("1000", "SIP", "outbound")
                
                if result["success"]:
                    print(f"✅ Call origination successful: {result['call_id']}")
                    
                    # Wait a bit then hangup
                    await asyncio.sleep(3)
                    await ami.hangup_call(result['call_id'])
                    print("📞 Call ended")
                else:
                    print(f"❌ Call origination failed: {result['error']}")
                
            else:
                print("❌ Authentication failed")
                print("   Check username/password in manager.conf")
            
            await ami.disconnect()
        else:
            print("❌ Connection failed")
            print("   Check if Asterisk is running: sudo systemctl status asterisk")
            print("   Check AMI configuration in manager.conf")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure Asterisk is installed and running")
        print("2. Check manager.conf configuration")
        print("3. Verify firewall allows port 5038")
        print("4. See docs/ASTERISK_SETUP.md for detailed setup")


async def main():
    """Main demo function"""
    print("🎯 AI Cold Calling Agent - Asterisk Integration Examples")
    print("=" * 60)
    print("This demo shows how to integrate the AI agent with Asterisk PBX:")
    print("- Direct AMI (Asterisk Manager Interface) integration")
    print("- Call origination and management")
    print("- Real-time call event handling")
    print("- Full AI agent with Asterisk telephony")
    print()
    
    # Run configuration test first
    await asterisk_configuration_test()
    
    # Ask user which demo to run
    print(f"\n❓ Which demo would you like to run?")
    print("   1. Asterisk integration demo (AMI only)")
    print("   2. Full AI agent with Asterisk demo")
    print("   3. Skip demos (configuration test only)")
    
    try:
        choice = input("   Enter choice (1-3): ").strip()
        
        if choice == "1":
            await asterisk_integration_demo()
        elif choice == "2":
            await full_asterisk_agent_demo()
        else:
            print("   Demos skipped. See docs/ASTERISK_SETUP.md for configuration help.")
            
    except KeyboardInterrupt:
        print("\n   Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    
    print(f"\n✅ Asterisk integration examples completed!")
    print("📖 For detailed setup instructions, see docs/ASTERISK_SETUP.md")


if __name__ == "__main__":
    asyncio.run(main())