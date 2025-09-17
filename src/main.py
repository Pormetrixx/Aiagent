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
            # Convert bytes to numpy array (implementation depends on audio format)
            # For now, we'll simulate the transcription
            return {
                "text": "Simulated customer response",
                "confidence": 0.9
            }
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return {"text": "", "confidence": 0.0}
    
    async def _speak_text(self, text: str):
        """Convert text to speech and play"""
        if not self.tts_engine:
            logger.info(f"TTS not available, would speak: {text}")
            return
        
        try:
            # Generate speech
            audio_output = self.tts_engine.synthesize(text)
            
            # In a real implementation, this would play the audio
            logger.info(f"Speaking: {text}")
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
    
    async def _end_call(self, call_id: str, outcome: str):
        """End a call and clean up"""
        if call_id in self.active_calls:
            call_info = self.active_calls[call_id]
            
            # End conversation
            self.conversation_manager.end_conversation(call_id, outcome)
            
            # Generate training data if trainer is available
            if self.trainer:
                # This would typically extract conversation turns and generate training data
                pass
            
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