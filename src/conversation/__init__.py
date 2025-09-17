"""
Conversation management module for the AI Cold Calling Agent
"""
from .state_machine import ConversationStateMachine, ConversationState, ConversationTrigger, ConversationContext, create_conversation_state_machine
from .manager import ConversationManager, ResponseGenerator, create_conversation_manager
from .emotion_recognition import EmotionRecognitionSystem, TextEmotionAnalyzer, AudioEmotionAnalyzer, FacialEmotionAnalyzer, create_emotion_recognition_system

__all__ = [
    'ConversationStateMachine', 'ConversationState', 'ConversationTrigger', 'ConversationContext',
    'create_conversation_state_machine', 'ConversationManager', 'ResponseGenerator',
    'create_conversation_manager', 'EmotionRecognitionSystem', 'TextEmotionAnalyzer',
    'AudioEmotionAnalyzer', 'FacialEmotionAnalyzer', 'create_emotion_recognition_system'
]