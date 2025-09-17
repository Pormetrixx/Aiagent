"""
Main application for the AI Cold Calling Agent
"""
import logging
import asyncio
import signal
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from .config import create_config_manager
from .database import DatabaseManager, ConversationRepository, FAQRepository, ScriptRepository, TrainingRepository, CustomerRepository
from .speech import create_stt_engine, create_tts_engine
from .conversation import create_conversation_manager, create_emotion_recognition_system
from .training import create_continuous_trainer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AICallingAgent:
    """Main AI Cold Calling Agent application"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the AI calling agent
        
        Args:
            config_path: Path to configuration file
        """
        self.config_manager = create_config_manager(config_path)
        
        # Validate configuration
        if not self.config_manager.is_valid():
            errors = self.config_manager.validate_config()
            logger.error(f"Configuration validation failed: {errors}")
            raise ValueError("Invalid configuration")
        
        # Initialize components
        self.db_manager = None
        self.stt_engine = None
        self.tts_engine = None
        self.emotion_system = None
        self.conversation_manager = None
        self.trainer = None
        
        # Component repositories
        self.conversation_repo = None
        self.faq_repo = None
        self.script_repo = None
        self.training_repo = None
        self.customer_repo = None
        
        # Application state
        self.is_running = False
        self.active_calls = {}
        
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config_manager.get_section("logging")
        log_level = log_config.get("level", "INFO")
        log_file = log_config.get("file_path", "logs/aiagent.log")
        
        # Create logs directory
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level))
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        root_logger.setLevel(getattr(logging, log_level))
        
        logger.info(f"Logging configured: level={log_level}, file={log_file}")
    
    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing AI Cold Calling Agent...")
        
        try:
            # Initialize database
            await self._initialize_database()
            
            # Initialize speech components
            await self._initialize_speech_components()
            
            # Initialize conversation system
            await self._initialize_conversation_system()
            
            # Initialize training system
            await self._initialize_training_system()
            
            logger.info("AI Cold Calling Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise
    
    async def _initialize_database(self):
        """Initialize database connection and repositories"""
        logger.info("Initializing database...")
        
        # Create database manager
        database_url = self.config_manager.get_database_url()
        echo = self.config_manager.get("database", "echo", False)
        pool_size = self.config_manager.get("database", "pool_size", 5)
        
        self.db_manager = DatabaseManager(database_url, echo, pool_size)
        
        # Test connection
        if not self.db_manager.test_connection():
            raise RuntimeError("Database connection failed")
        
        # Create tables
        self.db_manager.create_tables()
        
        # Initialize repositories
        self.conversation_repo = ConversationRepository(self.db_manager)
        self.faq_repo = FAQRepository(self.db_manager)
        self.script_repo = ScriptRepository(self.db_manager)
        self.training_repo = TrainingRepository(self.db_manager)
        self.customer_repo = CustomerRepository(self.db_manager)
        
        logger.info("Database initialized successfully")
    
    async def _initialize_speech_components(self):
        """Initialize speech recognition and synthesis"""
        logger.info("Initializing speech components...")
        
        # Initialize STT
        stt_config = self.config_manager.get_section("speech_recognition")
        self.stt_engine = create_stt_engine(stt_config)
        
        if not self.stt_engine.is_available():
            logger.warning("STT engine not available")
        
        # Initialize TTS
        tts_config = self.config_manager.get_section("text_to_speech")
        self.tts_engine = create_tts_engine(tts_config)
        
        if not self.tts_engine.is_available():
            logger.warning("TTS engine not available")
        
        logger.info("Speech components initialized")
    
    async def _initialize_conversation_system(self):
        """Initialize conversation management system"""
        logger.info("Initializing conversation system...")
        
        # Initialize emotion recognition
        emotion_config = self.config_manager.get_section("emotion_recognition")
        self.emotion_system = create_emotion_recognition_system(emotion_config)
        
        # Initialize conversation manager
        self.conversation_manager = create_conversation_manager(
            self.conversation_repo,
            self.faq_repo,
            self.script_repo
        )
        
        logger.info("Conversation system initialized")
    
    async def _initialize_training_system(self):
        """Initialize training and continuous improvement system"""
        logger.info("Initializing training system...")
        
        training_config = self.config_manager.get_section("training")
        
        if training_config.get("enabled", True):
            self.trainer = create_continuous_trainer(
                self.training_repo,
                self.conversation_repo
            )
            logger.info("Training system initialized")
        else:
            logger.info("Training system disabled")
    
    async def start_call(self, customer_phone: str, customer_name: Optional[str] = None) -> str:
        """
        Start a new call
        
        Args:
            customer_phone: Customer phone number
            customer_name: Customer name (optional)
            
        Returns:
            Call ID
        """
        call_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting call {call_id} to {customer_phone}")
            
            # Check if customer is on do-not-call list
            customer = self.customer_repo.get_customer_by_phone(customer_phone)
            if customer and customer.do_not_call:
                raise ValueError("Customer is on do-not-call list")
            
            # Initialize actual phone call (placeholder for real telephony integration)
            call_success = await self._initiate_phone_call(customer_phone)
            if not call_success:
                raise RuntimeError(f"Failed to establish phone connection to {customer_phone}")
            
            # Start conversation
            conversation_result = self.conversation_manager.start_conversation(
                call_id=call_id,
                customer_phone=customer_phone,
                customer_name=customer_name
            )
            
            # Store call in active calls
            self.active_calls[call_id] = {
                "start_time": datetime.utcnow(),
                "customer_phone": customer_phone,
                "customer_name": customer_name,
                "conversation_id": conversation_result["conversation_id"]
            }
            
            # Generate and play opening message
            opening_text = conversation_result["response"]
            await self._speak_text(opening_text)
            
            logger.info(f"Call {call_id} started successfully")
            return call_id
            
        except Exception as e:
            logger.error(f"Failed to start call {call_id}: {e}")
            raise
    
    async def process_audio_input(self, call_id: str, audio_data: bytes) -> Dict[str, Any]:
        """
        Process audio input from customer
        
        Args:
            call_id: Call identifier
            audio_data: Audio data from customer
            
        Returns:
            Processing results including agent response
        """
        if call_id not in self.active_calls:
            raise ValueError(f"No active call found: {call_id}")
        
        try:
            # Convert audio to text
            stt_result = await self._transcribe_audio(audio_data)
            customer_text = stt_result["text"]
            confidence = stt_result["confidence"]
            
            logger.debug(f"Call {call_id} - Customer: {customer_text}")
            
            # Analyze emotion
            emotion_result = None
            if self.emotion_system:
                emotion_result = self.emotion_system.analyze_multimodal_emotion(text=customer_text)
                emotion = emotion_result["smoothed_emotion"]["primary_emotion"]
            else:
                emotion = "neutral"
            
            # Process through conversation manager
            conversation_result = self.conversation_manager.process_customer_input(
                call_id=call_id,
                customer_input=customer_text,
                emotion=emotion,
                confidence_score=confidence
            )
            
            # Generate agent response
            agent_response = conversation_result["response"]
            
            # Speak agent response
            await self._speak_text(agent_response)
            
            # Check if call should end
            if conversation_result["should_end"]:
                await self._end_call(call_id, conversation_result["outcome"])
            
            logger.debug(f"Call {call_id} - Agent: {agent_response}")
            
            return {
                "call_id": call_id,
                "customer_text": customer_text,
                "agent_response": agent_response,
                "emotion": emotion,
                "confidence": confidence,
                "conversation_state": conversation_result["state"],
                "should_end": conversation_result["should_end"],
                "outcome": conversation_result.get("outcome")
            }
            
        except Exception as e:
            logger.error(f"Error processing audio input for call {call_id}: {e}")
            raise
    
    async def _transcribe_audio(self, audio_data: bytes) -> Dict[str, Any]:
        """Transcribe audio to text"""
        if not self.stt_engine:
            return {"text": "", "confidence": 0.0}
        
        try:
            import numpy as np
            import tempfile
            import os
            
            # Convert bytes to audio file for Whisper processing
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Use Whisper to transcribe the audio file
                result = self.stt_engine.transcribe_file(temp_file_path)
                return {
                    "text": result.get("text", ""),
                    "confidence": result.get("confidence", 0.0)
                }
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return {"text": "", "confidence": 0.0}
    
    async def _speak_text(self, text: str):
        """Convert text to speech and play"""
        if not self.tts_engine:
            logger.info(f"TTS not available, would speak: {text}")
            return
        
        try:
            import tempfile
            import os
            import subprocess
            import platform
            
            # Generate speech to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file_path = temp_file.name
            
            try:
                # Synthesize speech to file
                self.tts_engine.synthesize(text, temp_file_path)
                
                # Play the audio file using system audio player
                system = platform.system().lower()
                if system == "linux":
                    # Use aplay on Linux (common on Ubuntu)
                    subprocess.run(["aplay", temp_file_path], 
                                 capture_output=True, check=False)
                elif system == "darwin":
                    # Use afplay on macOS
                    subprocess.run(["afplay", temp_file_path], 
                                 capture_output=True, check=False)
                elif system == "windows":
                    # Use Windows Media Player on Windows
                    subprocess.run(["start", "/wait", temp_file_path], 
                                 shell=True, capture_output=True, check=False)
                else:
                    logger.warning(f"Audio playback not supported on {system}")
                
                logger.debug(f"Spoke text: {text[:50]}...")
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            # Fallback: just log the text
            logger.info(f"Would speak: {text}")
    
    async def _initiate_phone_call(self, phone_number: str) -> bool:
        """
        Initiate an actual phone call
        
        This is a placeholder for real telephony integration.
        In production, this would integrate with:
        - Twilio API for cloud-based calling
        - Asterisk/FreePBX for on-premise PBX
        - SIP providers for VoIP calling
        - Hardware telephony cards for PSTN
        
        Args:
            phone_number: Target phone number
            
        Returns:
            True if call was successfully initiated, False otherwise
        """
        try:
            # Validate phone number format
            import re
            phone_pattern = r'^\+?[1-9]\d{1,14}$'  # International format
            if not re.match(phone_pattern, phone_number.replace(' ', '').replace('-', '')):
                logger.error(f"Invalid phone number format: {phone_number}")
                return False
            
            # Placeholder for actual telephony integration
            # Example integrations:
            
            # 1. Twilio integration:
            # from twilio.rest import Client
            # client = Client(account_sid, auth_token)
            # call = client.calls.create(
            #     to=phone_number,
            #     from_=twilio_phone_number,
            #     url=webhook_url_for_twiml
            # )
            
            # 2. Asterisk AMI integration:
            # import asterisk.manager
            # manager = asterisk.manager.Manager()
            # manager.connect(host, port, username, password)
            # manager.originate(
            #     channel=f"SIP/{phone_number}",
            #     context="default",
            #     exten="s",
            #     priority=1
            # )
            
            # 3. SIP integration with pjsua:
            # import pjsua as pj
            # lib = pj.Lib()
            # lib.init()
            # transport = lib.create_transport(pj.TransportType.UDP)
            # acc = lib.create_account_for_transport(transport)
            # call = acc.make_call(f"sip:{phone_number}@provider.com")
            
            # For development/testing, simulate successful call initiation
            logger.info(f"Simulating phone call to {phone_number}")
            await asyncio.sleep(0.1)  # Simulate connection delay
            
            # In a real implementation, this would return the actual success status
            return True
            
        except Exception as e:
            logger.error(f"Error initiating phone call to {phone_number}: {e}")
            return False
    
    async def start_listening_for_customer_input(self, call_id: str, duration_seconds: int = 10) -> bytes:
        """
        Listen for customer audio input during an active call
        
        Args:
            call_id: Active call identifier
            duration_seconds: How long to listen for input
            
        Returns:
            Raw audio data as bytes
        """
        if call_id not in self.active_calls:
            raise ValueError(f"No active call found: {call_id}")
        
        try:
            import pyaudio
            import wave
            import tempfile
            
            # Audio configuration
            chunk = 1024
            sample_format = pyaudio.paInt16
            channels = 1
            fs = 16000  # Sample rate for speech recognition
            
            p = pyaudio.PyAudio()
            
            logger.debug(f"Starting to listen for customer input on call {call_id}")
            
            # Start recording
            stream = p.open(format=sample_format,
                          channels=channels,
                          rate=fs,
                          frames_per_buffer=chunk,
                          input=True)
            
            frames = []
            
            # Record for specified duration
            for i in range(0, int(fs / chunk * duration_seconds)):
                data = stream.read(chunk)
                frames.append(data)
            
            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Convert frames to bytes
            with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
                wf = wave.open(temp_file.name, 'wb')
                wf.setnchannels(channels)
                wf.setsampwidth(p.get_sample_size(sample_format))
                wf.setframerate(fs)
                wf.writeframes(b''.join(frames))
                wf.close()
                
                # Read the audio file as bytes
                with open(temp_file.name, 'rb') as f:
                    audio_data = f.read()
            
            logger.debug(f"Captured {len(audio_data)} bytes of audio from call {call_id}")
            return audio_data
            
        except ImportError:
            logger.warning("PyAudio not available - cannot capture real audio input")
            # Return empty audio data
            return b''
        except Exception as e:
            logger.error(f"Error capturing audio input for call {call_id}: {e}")
            return b''
    
    async def _end_call(self, call_id: str, outcome: str):
        """End a call and clean up"""
        if call_id in self.active_calls:
            call_info = self.active_calls[call_id]
            
            # End conversation
            self.conversation_manager.end_conversation(call_id, outcome)
            
            # Generate training data if trainer is available
            if self.trainer:
                try:
                    # Get conversation data
                    conversation = self.conversation_repo.get_conversation(call_id)
                    if conversation:
                        # Get conversation turns
                        conversation_turns = self.conversation_repo.get_conversation_turns(conversation.id)
                        
                        # Convert turns to format expected by trainer
                        turn_data = []
                        for turn in conversation_turns:
                            turn_data.append({
                                "speaker": turn.speaker,
                                "text_content": turn.text_content,
                                "emotion": turn.emotion,
                                "confidence_score": turn.confidence_score,
                                "timestamp": turn.timestamp,
                                "response_time_ms": turn.response_time_ms
                            })
                        
                        # Generate training data from the conversation
                        self.trainer.data_generator.generate_training_data_from_conversation(
                            conversation.id, turn_data, outcome
                        )
                        
                        logger.debug(f"Generated training data for conversation {conversation.id}")
                        
                except Exception as e:
                    logger.error(f"Error generating training data for call {call_id}: {e}")
            
            # Remove from active calls
            del self.active_calls[call_id]
            
            logger.info(f"Call {call_id} ended with outcome: {outcome}")
    
    async def get_call_status(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a call"""
        if call_id not in self.active_calls:
            return None
        
        call_info = self.active_calls[call_id]
        conversation_state = self.conversation_manager.get_conversation_state(call_id)
        
        return {
            "call_id": call_id,
            "start_time": call_info["start_time"],
            "customer_phone": call_info["customer_phone"],
            "customer_name": call_info["customer_name"],
            "conversation_state": conversation_state,
            "duration": (datetime.utcnow() - call_info["start_time"]).total_seconds()
        }
    
    async def run_training_cycle(self) -> Dict[str, Any]:
        """Run a training cycle"""
        if not self.trainer:
            return {"status": "disabled", "message": "Training is disabled"}
        
        try:
            return self.trainer.execute_training_cycle()
        except Exception as e:
            logger.error(f"Training cycle failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "running": self.is_running,
            "active_calls": len(self.active_calls),
            "components": {
                "database": self.db_manager.test_connection() if self.db_manager else False,
                "stt": self.stt_engine.is_available() if self.stt_engine else False,
                "tts": self.tts_engine.is_available() if self.tts_engine else False,
                "emotion_recognition": self.emotion_system.is_available() if self.emotion_system else {},
                "training": self.trainer is not None
            },
            "configuration": {
                "database_type": self.config_manager.get("database", "type"),
                "stt_engine": self.config_manager.get("speech_recognition", "engine"),
                "tts_engine": self.config_manager.get("text_to_speech", "engine")
            }
        }
    
    async def start(self):
        """Start the application"""
        if self.is_running:
            logger.warning("Agent is already running")
            return
        
        await self.initialize()
        self.is_running = True
        
        logger.info("AI Cold Calling Agent started")
        
        # Setup signal handlers for graceful shutdown
        loop = asyncio.get_event_loop()
        for sig in [signal.SIGTERM, signal.SIGINT]:
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
    
    async def stop(self):
        """Stop the application"""
        if not self.is_running:
            return
        
        logger.info("Stopping AI Cold Calling Agent...")
        
        # End all active calls
        for call_id in list(self.active_calls.keys()):
            await self._end_call(call_id, "system_shutdown")
        
        # Clean up resources
        self.is_running = False
        
        logger.info("AI Cold Calling Agent stopped")


async def main():
    """Main application entry point"""
    try:
        # Create and start the agent
        agent = AICallingAgent()
        await agent.start()
        
        # Keep running until stopped
        while agent.is_running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise
    finally:
        if 'agent' in locals():
            await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())