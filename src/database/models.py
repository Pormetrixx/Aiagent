"""
Database models for the AI Cold Calling Agent
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, 
    DateTime, Time, ForeignKey, ARRAY, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func

Base = declarative_base()


class Conversation(Base):
    """Model for storing conversation data"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    call_id = Column(String(255), unique=True, nullable=False)
    customer_phone = Column(String(20))
    customer_name = Column(String(255))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)
    status = Column(String(50), nullable=False)  # active, completed, failed, abandoned
    outcome = Column(String(100))  # appointment, callback, not_interested, invalid_number
    emotion_score = Column(Float)
    sentiment_score = Column(Float)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    turns = relationship("ConversationTurn", back_populates="conversation", cascade="all, delete-orphan")
    metrics = relationship("CallMetric", back_populates="conversation", cascade="all, delete-orphan")
    training_data = relationship("TrainingData", back_populates="conversation")


class ConversationTurn(Base):
    """Model for storing individual conversation exchanges"""
    __tablename__ = 'conversation_turns'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'))
    turn_number = Column(Integer, nullable=False)
    speaker = Column(String(20), nullable=False)  # agent or customer
    text_content = Column(Text, nullable=False)
    audio_file_path = Column(String(500))
    emotion = Column(String(50))
    confidence_score = Column(Float)
    timestamp = Column(DateTime, nullable=False)
    response_time_ms = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="turns")


class FAQEntry(Base):
    """Model for FAQ and knowledge base entries"""
    __tablename__ = 'faq_entries'
    
    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100))
    keywords = Column(ARRAY(String))
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    language = Column(String(10), default='de')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ConversationScript(Base):
    """Model for conversation scripts and templates"""
    __tablename__ = 'conversation_scripts'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    script_type = Column(String(50), nullable=False)  # opening, objection_handling, closing
    content = Column(Text, nullable=False)
    variables = Column(JSON)
    success_rate = Column(Float, default=0.0)
    usage_count = Column(Integer, default=0)
    language = Column(String(10), default='de')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class TrainingData(Base):
    """Model for storing training data for continuous improvement"""
    __tablename__ = 'training_data'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    input_text = Column(Text, nullable=False)
    expected_response = Column(Text, nullable=False)
    actual_response = Column(Text)
    feedback_score = Column(Integer)  # 1-5 rating
    emotion_context = Column(String(50))
    improvement_suggestions = Column(Text)
    is_used_for_training = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="training_data")


class CallMetric(Base):
    """Model for storing call metrics and analytics"""
    __tablename__ = 'call_metrics'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'))
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50))  # emotion, sentiment, engagement, conversion
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="metrics")


class Customer(Base):
    """Model for customer information and preferences"""
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), unique=True, nullable=False)
    name = Column(String(255))
    email = Column(String(255))
    preferred_language = Column(String(10), default='de')
    timezone = Column(String(50))
    best_call_time = Column(Time)
    do_not_call = Column(Boolean, default=False)
    notes = Column(Text)
    last_contact = Column(DateTime)
    conversion_probability = Column(Float)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class SystemSetting(Base):
    """Model for system configuration and settings"""
    __tablename__ = 'system_settings'
    
    id = Column(Integer, primary_key=True)
    setting_key = Column(String(255), unique=True, nullable=False)
    setting_value = Column(Text, nullable=False)
    setting_type = Column(String(50), nullable=False)  # string, integer, float, boolean, json
    description = Column(Text)
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())