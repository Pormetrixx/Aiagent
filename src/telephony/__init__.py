"""
Telephony integration module for the AI Cold Calling Agent
"""
from .asterisk import AsteriskAMIManager, AsteriskTelephonyProvider, create_asterisk_provider

__all__ = [
    'AsteriskAMIManager', 'AsteriskTelephonyProvider', 'create_asterisk_provider'
]