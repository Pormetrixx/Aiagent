"""
AI Cold Calling Agent - Main package
"""
from .main import AICallingAgent
from .config import ConfigManager, create_config_manager

__version__ = "1.0.0"
__author__ = "AI Cold Calling Agent Team"

__all__ = [
    'AICallingAgent', 'ConfigManager', 'create_config_manager'
]