"""
Database module for the AI Cold Calling Agent
"""
from .models import (
    Base, Conversation, ConversationTurn, FAQEntry, 
    ConversationScript, TrainingData, CallMetric, 
    Customer, SystemSetting
)
from .operations import (
    DatabaseManager, ConversationRepository, FAQRepository,
    ScriptRepository, TrainingRepository, CustomerRepository
)

__all__ = [
    'Base', 'Conversation', 'ConversationTurn', 'FAQEntry',
    'ConversationScript', 'TrainingData', 'CallMetric',
    'Customer', 'SystemSetting', 'DatabaseManager',
    'ConversationRepository', 'FAQRepository', 'ScriptRepository',
    'TrainingRepository', 'CustomerRepository'
]