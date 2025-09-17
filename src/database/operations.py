"""
Database connection and operations for the AI Cold Calling Agent
"""
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from .models import Base, Conversation, ConversationTurn, FAQEntry, ConversationScript, TrainingData, CallMetric, Customer, SystemSetting

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, database_url: str, echo: bool = False, pool_size: int = 5):
        """
        Initialize database manager
        
        Args:
            database_url: Database connection URL
            echo: Whether to echo SQL statements
            pool_size: Connection pool size
        """
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            echo=echo,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=10,
            pool_pre_ping=True
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Get database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


class ConversationRepository:
    """Repository for conversation-related database operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_conversation(self, call_id: str, customer_phone: str, 
                          customer_name: Optional[str] = None) -> Conversation:
        """Create a new conversation record"""
        with self.db_manager.get_session() as session:
            conversation = Conversation(
                call_id=call_id,
                customer_phone=customer_phone,
                customer_name=customer_name,
                start_time=datetime.utcnow(),
                status='active'
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            return conversation
    
    def add_conversation_turn(self, conversation_id: int, speaker: str, 
                            text_content: str, emotion: Optional[str] = None,
                            confidence_score: Optional[float] = None,
                            audio_file_path: Optional[str] = None) -> ConversationTurn:
        """Add a turn to an existing conversation"""
        with self.db_manager.get_session() as session:
            # Get the next turn number
            max_turn = session.query(func.max(ConversationTurn.turn_number))\
                            .filter(ConversationTurn.conversation_id == conversation_id)\
                            .scalar() or 0
            
            turn = ConversationTurn(
                conversation_id=conversation_id,
                turn_number=max_turn + 1,
                speaker=speaker,
                text_content=text_content,
                emotion=emotion,
                confidence_score=confidence_score,
                audio_file_path=audio_file_path,
                timestamp=datetime.utcnow()
            )
            session.add(turn)
            session.commit()
            session.refresh(turn)
            return turn
    
    def end_conversation(self, conversation_id: int, outcome: str, 
                        emotion_score: Optional[float] = None,
                        sentiment_score: Optional[float] = None):
        """End a conversation and update its status"""
        with self.db_manager.get_session() as session:
            conversation = session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if conversation:
                conversation.end_time = datetime.utcnow()
                conversation.status = 'completed'
                conversation.outcome = outcome
                conversation.emotion_score = emotion_score
                conversation.sentiment_score = sentiment_score
                
                if conversation.start_time:
                    duration = conversation.end_time - conversation.start_time
                    conversation.duration_seconds = int(duration.total_seconds())
                
                session.commit()
    
    def get_conversation(self, call_id: str) -> Optional[Conversation]:
        """Get conversation by call ID"""
        with self.db_manager.get_session() as session:
            return session.query(Conversation).filter(
                Conversation.call_id == call_id
            ).first()
    
    def get_conversation_turns(self, conversation_id: int) -> List[ConversationTurn]:
        """Get all turns for a conversation"""
        with self.db_manager.get_session() as session:
            return session.query(ConversationTurn)\
                         .filter(ConversationTurn.conversation_id == conversation_id)\
                         .order_by(ConversationTurn.turn_number)\
                         .all()


class FAQRepository:
    """Repository for FAQ and knowledge base operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def search_faq(self, query: str, language: str = 'de', limit: int = 5) -> List[FAQEntry]:
        """Search FAQ entries by keywords"""
        with self.db_manager.get_session() as session:
            # Simple keyword matching - can be enhanced with full-text search
            query_lower = query.lower()
            
            return session.query(FAQEntry)\
                         .filter(FAQEntry.is_active == True)\
                         .filter(FAQEntry.language == language)\
                         .filter(FAQEntry.keywords.op('&&')(func.array([query_lower])))\
                         .order_by(FAQEntry.usage_count.desc())\
                         .limit(limit)\
                         .all()
    
    def get_faq_by_category(self, category: str, language: str = 'de') -> List[FAQEntry]:
        """Get FAQ entries by category"""
        with self.db_manager.get_session() as session:
            return session.query(FAQEntry)\
                         .filter(FAQEntry.category == category)\
                         .filter(FAQEntry.language == language)\
                         .filter(FAQEntry.is_active == True)\
                         .order_by(FAQEntry.usage_count.desc())\
                         .all()
    
    def increment_faq_usage(self, faq_id: int):
        """Increment usage count for an FAQ entry"""
        with self.db_manager.get_session() as session:
            faq = session.query(FAQEntry).filter(FAQEntry.id == faq_id).first()
            if faq:
                faq.usage_count += 1
                session.commit()


class ScriptRepository:
    """Repository for conversation script operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_script_by_type(self, script_type: str, language: str = 'de') -> Optional[ConversationScript]:
        """Get a conversation script by type"""
        with self.db_manager.get_session() as session:
            return session.query(ConversationScript)\
                         .filter(ConversationScript.script_type == script_type)\
                         .filter(ConversationScript.language == language)\
                         .filter(ConversationScript.is_active == True)\
                         .order_by(ConversationScript.success_rate.desc())\
                         .first()
    
    def get_all_scripts(self, language: str = 'de') -> List[ConversationScript]:
        """Get all active conversation scripts"""
        with self.db_manager.get_session() as session:
            return session.query(ConversationScript)\
                         .filter(ConversationScript.language == language)\
                         .filter(ConversationScript.is_active == True)\
                         .order_by(ConversationScript.script_type, ConversationScript.success_rate.desc())\
                         .all()


class TrainingRepository:
    """Repository for training data operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def add_training_data(self, conversation_id: int, input_text: str, 
                         expected_response: str, actual_response: str,
                         feedback_score: Optional[int] = None,
                         emotion_context: Optional[str] = None) -> TrainingData:
        """Add training data from a conversation"""
        with self.db_manager.get_session() as session:
            training_data = TrainingData(
                conversation_id=conversation_id,
                input_text=input_text,
                expected_response=expected_response,
                actual_response=actual_response,
                feedback_score=feedback_score,
                emotion_context=emotion_context
            )
            session.add(training_data)
            session.commit()
            session.refresh(training_data)
            return training_data
    
    def get_training_data(self, limit: int = 1000, used_for_training: bool = False) -> List[TrainingData]:
        """Get training data for model improvement"""
        with self.db_manager.get_session() as session:
            return session.query(TrainingData)\
                         .filter(TrainingData.is_used_for_training == used_for_training)\
                         .order_by(TrainingData.feedback_score.desc())\
                         .limit(limit)\
                         .all()
    
    def mark_training_data_used(self, training_data_ids: List[int]):
        """Mark training data as used"""
        with self.db_manager.get_session() as session:
            session.query(TrainingData)\
                   .filter(TrainingData.id.in_(training_data_ids))\
                   .update({TrainingData.is_used_for_training: True})
            session.commit()


class CustomerRepository:
    """Repository for customer data operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_customer_by_phone(self, phone_number: str) -> Optional[Customer]:
        """Get customer by phone number"""
        with self.db_manager.get_session() as session:
            return session.query(Customer)\
                         .filter(Customer.phone_number == phone_number)\
                         .first()
    
    def create_or_update_customer(self, phone_number: str, **kwargs) -> Customer:
        """Create or update customer information"""
        with self.db_manager.get_session() as session:
            customer = session.query(Customer)\
                             .filter(Customer.phone_number == phone_number)\
                             .first()
            
            if customer:
                for key, value in kwargs.items():
                    if hasattr(customer, key):
                        setattr(customer, key, value)
            else:
                customer = Customer(phone_number=phone_number, **kwargs)
                session.add(customer)
            
            session.commit()
            session.refresh(customer)
            return customer