"""
Conversation state machine for managing call flow
"""
import logging
from enum import Enum
from typing import Dict, Any, Optional, Callable, List
from transitions import Machine
from datetime import datetime

logger = logging.getLogger(__name__)


class ConversationState(Enum):
    """Conversation states"""
    INITIAL = "initial"
    OPENING = "opening"
    INTRODUCING = "introducing"
    QUESTIONING = "questioning"
    PRESENTING = "presenting"
    HANDLING_OBJECTIONS = "handling_objections"
    CLOSING = "closing"
    SCHEDULING = "scheduling"
    ENDING = "ending"
    FAILED = "failed"
    COMPLETED = "completed"


class ConversationTrigger(Enum):
    """Conversation triggers/events"""
    START_CALL = "start_call"
    CUSTOMER_ANSWERED = "customer_answered"
    INTRODUCTION_DONE = "introduction_done"
    INTEREST_SHOWN = "interest_shown"
    OBJECTION_RAISED = "objection_raised"
    OBJECTION_HANDLED = "objection_handled"
    READY_TO_CLOSE = "ready_to_close"
    APPOINTMENT_REQUESTED = "appointment_requested"
    APPOINTMENT_SCHEDULED = "appointment_scheduled"
    CUSTOMER_NOT_INTERESTED = "customer_not_interested"
    CALL_FAILED = "call_failed"
    CALL_ENDED = "call_ended"


class ConversationContext:
    """Context data for conversation state"""
    
    def __init__(self):
        self.customer_name: Optional[str] = None
        self.customer_phone: Optional[str] = None
        self.customer_emotion: Optional[str] = None
        self.conversation_history: List[Dict[str, Any]] = []
        self.objections_count: int = 0
        self.interest_level: float = 0.0
        self.call_start_time: Optional[datetime] = None
        self.current_script_type: Optional[str] = None
        self.appointment_time: Optional[str] = None
        self.custom_data: Dict[str, Any] = {}
    
    def add_turn(self, speaker: str, text: str, emotion: Optional[str] = None):
        """Add a conversation turn to history"""
        turn = {
            "speaker": speaker,
            "text": text,
            "emotion": emotion,
            "timestamp": datetime.utcnow()
        }
        self.conversation_history.append(turn)
    
    def get_last_customer_input(self) -> Optional[str]:
        """Get the last customer input"""
        for turn in reversed(self.conversation_history):
            if turn["speaker"] == "customer":
                return turn["text"]
        return None
    
    def get_conversation_duration(self) -> Optional[float]:
        """Get conversation duration in seconds"""
        if self.call_start_time:
            return (datetime.utcnow() - self.call_start_time).total_seconds()
        return None


class ConversationStateMachine:
    """State machine for managing conversation flow"""
    
    def __init__(self):
        self.context = ConversationContext()
        self.callbacks: Dict[str, List[Callable]] = {}
        
        # Define state transitions
        self.transitions = [
            # From INITIAL
            {'trigger': ConversationTrigger.START_CALL.value, 'source': ConversationState.INITIAL.value, 'dest': ConversationState.OPENING.value},
            
            # From OPENING
            {'trigger': ConversationTrigger.CUSTOMER_ANSWERED.value, 'source': ConversationState.OPENING.value, 'dest': ConversationState.INTRODUCING.value},
            {'trigger': ConversationTrigger.CALL_FAILED.value, 'source': ConversationState.OPENING.value, 'dest': ConversationState.FAILED.value},
            
            # From INTRODUCING
            {'trigger': ConversationTrigger.INTRODUCTION_DONE.value, 'source': ConversationState.INTRODUCING.value, 'dest': ConversationState.QUESTIONING.value},
            {'trigger': ConversationTrigger.CUSTOMER_NOT_INTERESTED.value, 'source': ConversationState.INTRODUCING.value, 'dest': ConversationState.HANDLING_OBJECTIONS.value},
            {'trigger': ConversationTrigger.CALL_ENDED.value, 'source': ConversationState.INTRODUCING.value, 'dest': ConversationState.ENDING.value},
            
            # From QUESTIONING
            {'trigger': ConversationTrigger.INTEREST_SHOWN.value, 'source': ConversationState.QUESTIONING.value, 'dest': ConversationState.PRESENTING.value},
            {'trigger': ConversationTrigger.OBJECTION_RAISED.value, 'source': ConversationState.QUESTIONING.value, 'dest': ConversationState.HANDLING_OBJECTIONS.value},
            {'trigger': ConversationTrigger.READY_TO_CLOSE.value, 'source': ConversationState.QUESTIONING.value, 'dest': ConversationState.CLOSING.value},
            
            # From PRESENTING
            {'trigger': ConversationTrigger.READY_TO_CLOSE.value, 'source': ConversationState.PRESENTING.value, 'dest': ConversationState.CLOSING.value},
            {'trigger': ConversationTrigger.OBJECTION_RAISED.value, 'source': ConversationState.PRESENTING.value, 'dest': ConversationState.HANDLING_OBJECTIONS.value},
            
            # From HANDLING_OBJECTIONS
            {'trigger': ConversationTrigger.OBJECTION_HANDLED.value, 'source': ConversationState.HANDLING_OBJECTIONS.value, 'dest': ConversationState.PRESENTING.value},
            {'trigger': ConversationTrigger.CUSTOMER_NOT_INTERESTED.value, 'source': ConversationState.HANDLING_OBJECTIONS.value, 'dest': ConversationState.ENDING.value},
            {'trigger': ConversationTrigger.READY_TO_CLOSE.value, 'source': ConversationState.HANDLING_OBJECTIONS.value, 'dest': ConversationState.CLOSING.value},
            
            # From CLOSING
            {'trigger': ConversationTrigger.APPOINTMENT_REQUESTED.value, 'source': ConversationState.CLOSING.value, 'dest': ConversationState.SCHEDULING.value},
            {'trigger': ConversationTrigger.CUSTOMER_NOT_INTERESTED.value, 'source': ConversationState.CLOSING.value, 'dest': ConversationState.ENDING.value},
            
            # From SCHEDULING
            {'trigger': ConversationTrigger.APPOINTMENT_SCHEDULED.value, 'source': ConversationState.SCHEDULING.value, 'dest': ConversationState.COMPLETED.value},
            {'trigger': ConversationTrigger.CALL_FAILED.value, 'source': ConversationState.SCHEDULING.value, 'dest': ConversationState.ENDING.value},
            
            # Universal transitions
            {'trigger': ConversationTrigger.CALL_FAILED.value, 'source': '*', 'dest': ConversationState.FAILED.value},
            {'trigger': ConversationTrigger.CALL_ENDED.value, 'source': '*', 'dest': ConversationState.ENDING.value},
        ]
        
        # Initialize state machine
        self.machine = Machine(
            model=self,
            states=ConversationState,
            transitions=self.transitions,
            initial=ConversationState.INITIAL,
            auto_transitions=False
        )
        
        # Register state change callbacks
        self._register_state_callbacks()
    
    def _register_state_callbacks(self):
        """Register callbacks for state changes"""
        # Entry callbacks
        self.machine.add_transition('enter_opening', '*', ConversationState.OPENING.value, after='_on_enter_opening')
        self.machine.add_transition('enter_introducing', '*', ConversationState.INTRODUCING.value, after='_on_enter_introducing')
        self.machine.add_transition('enter_questioning', '*', ConversationState.QUESTIONING.value, after='_on_enter_questioning')
        self.machine.add_transition('enter_presenting', '*', ConversationState.PRESENTING.value, after='_on_enter_presenting')
        self.machine.add_transition('enter_handling_objections', '*', ConversationState.HANDLING_OBJECTIONS.value, after='_on_enter_handling_objections')
        self.machine.add_transition('enter_closing', '*', ConversationState.CLOSING.value, after='_on_enter_closing')
        self.machine.add_transition('enter_scheduling', '*', ConversationState.SCHEDULING.value, after='_on_enter_scheduling')
        self.machine.add_transition('enter_completed', '*', ConversationState.COMPLETED.value, after='_on_enter_completed')
        self.machine.add_transition('enter_failed', '*', ConversationState.FAILED.value, after='_on_enter_failed')
        self.machine.add_transition('enter_ending', '*', ConversationState.ENDING.value, after='_on_enter_ending')
    
    def register_callback(self, event: str, callback: Callable):
        """Register a callback for a specific event"""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
    
    def _trigger_callbacks(self, event: str, **kwargs):
        """Trigger all callbacks for an event"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(self.context, **kwargs)
                except Exception as e:
                    logger.error(f"Error in callback for {event}: {e}")
    
    def start_conversation(self, customer_phone: str, customer_name: Optional[str] = None):
        """Start a new conversation"""
        self.context = ConversationContext()
        self.context.customer_phone = customer_phone
        self.context.customer_name = customer_name
        self.context.call_start_time = datetime.utcnow()
        
        self.start_call()
    
    def process_customer_input(self, text: str, emotion: Optional[str] = None) -> str:
        """Process customer input and determine next action"""
        self.context.add_turn("customer", text, emotion)
        self.context.customer_emotion = emotion
        
        # Analyze input and trigger appropriate state change
        return self._analyze_input_and_transition(text, emotion)
    
    def _analyze_input_and_transition(self, text: str, emotion: Optional[str] = None) -> str:
        """Analyze customer input and trigger appropriate transition"""
        text_lower = text.lower()
        current_state = self.state
        
        # Basic intent recognition (this could be enhanced with NLP)
        if any(word in text_lower for word in ["nein", "nicht interessiert", "kein interesse", "nicht", "nee"]):
            if current_state in [ConversationState.INTRODUCING.value, ConversationState.QUESTIONING.value]:
                self.customer_not_interested()
                return "objection_detected"
            elif current_state == ConversationState.CLOSING.value:
                self.customer_not_interested()
                return "closing_rejected"
        
        elif any(word in text_lower for word in ["ja", "interessant", "mehr", "erzählen", "details"]):
            if current_state == ConversationState.INTRODUCING.value:
                self.introduction_done()
                return "introduction_accepted"
            elif current_state == ConversationState.QUESTIONING.value:
                self.interest_shown()
                return "interest_detected"
        
        elif any(word in text_lower for word in ["termin", "treffen", "gespräch", "meeting"]):
            if current_state in [ConversationState.PRESENTING.value, ConversationState.CLOSING.value]:
                self.appointment_requested()
                return "appointment_interest"
        
        elif any(word in text_lower for word in ["preis", "kosten", "teuer", "geld"]):
            if current_state in [ConversationState.PRESENTING.value, ConversationState.QUESTIONING.value]:
                self.objection_raised()
                self.context.objections_count += 1
                return "price_objection"
        
        elif any(word in text_lower for word in ["zeit", "keine zeit", "beschäftigt", "später"]):
            if current_state in [ConversationState.INTRODUCING.value, ConversationState.QUESTIONING.value]:
                self.objection_raised()
                self.context.objections_count += 1
                return "time_objection"
        
        # Default transitions based on current state
        if current_state == ConversationState.OPENING.value:
            self.customer_answered()
            return "customer_answered"
        elif current_state == ConversationState.INTRODUCING.value:
            self.introduction_done()
            return "introduction_done"
        elif current_state == ConversationState.QUESTIONING.value:
            self.interest_shown()
            return "questioning_done"
        elif current_state == ConversationState.PRESENTING.value:
            self.ready_to_close()
            return "ready_to_close"
        elif current_state == ConversationState.HANDLING_OBJECTIONS.value:
            self.objection_handled()
            return "objection_handled"
        elif current_state == ConversationState.SCHEDULING.value:
            self.appointment_scheduled()
            return "appointment_scheduled"
        
        return "continue_conversation"
    
    def get_current_script_type(self) -> str:
        """Get the appropriate script type for current state"""
        state_to_script = {
            ConversationState.OPENING.value: "opening",
            ConversationState.INTRODUCING.value: "opening",
            ConversationState.QUESTIONING.value: "questioning",
            ConversationState.PRESENTING.value: "presenting",
            ConversationState.HANDLING_OBJECTIONS.value: "objection_handling",
            ConversationState.CLOSING.value: "closing",
            ConversationState.SCHEDULING.value: "closing"
        }
        
        return state_to_script.get(self.state, "general")
    
    def is_conversation_ended(self) -> bool:
        """Check if conversation has ended"""
        return self.state in [ConversationState.COMPLETED.value, ConversationState.FAILED.value, ConversationState.ENDING.value]
    
    def get_conversation_outcome(self) -> str:
        """Get the conversation outcome"""
        if self.state == ConversationState.COMPLETED.value:
            return "appointment_scheduled"
        elif self.state == ConversationState.FAILED.value:
            return "call_failed"
        elif self.state == ConversationState.ENDING.value:
            if self.context.objections_count > 0:
                return "not_interested"
            return "call_ended"
        return "ongoing"
    
    # State entry callbacks
    def _on_enter_opening(self):
        logger.debug("Entering OPENING state")
        self.context.current_script_type = "opening"
        self._trigger_callbacks("enter_opening")
    
    def _on_enter_introducing(self):
        logger.debug("Entering INTRODUCING state")
        self.context.current_script_type = "opening"
        self._trigger_callbacks("enter_introducing")
    
    def _on_enter_questioning(self):
        logger.debug("Entering QUESTIONING state")
        self.context.current_script_type = "questioning"
        self._trigger_callbacks("enter_questioning")
    
    def _on_enter_presenting(self):
        logger.debug("Entering PRESENTING state")
        self.context.current_script_type = "presenting"
        self._trigger_callbacks("enter_presenting")
    
    def _on_enter_handling_objections(self):
        logger.debug("Entering HANDLING_OBJECTIONS state")
        self.context.current_script_type = "objection_handling"
        self._trigger_callbacks("enter_handling_objections")
    
    def _on_enter_closing(self):
        logger.debug("Entering CLOSING state")
        self.context.current_script_type = "closing"
        self._trigger_callbacks("enter_closing")
    
    def _on_enter_scheduling(self):
        logger.debug("Entering SCHEDULING state")
        self.context.current_script_type = "closing"
        self._trigger_callbacks("enter_scheduling")
    
    def _on_enter_completed(self):
        logger.debug("Entering COMPLETED state")
        self._trigger_callbacks("enter_completed")
    
    def _on_enter_failed(self):
        logger.debug("Entering FAILED state")
        self._trigger_callbacks("enter_failed")
    
    def _on_enter_ending(self):
        logger.debug("Entering ENDING state")
        self._trigger_callbacks("enter_ending")


def create_conversation_state_machine() -> ConversationStateMachine:
    """Factory function to create a conversation state machine"""
    return ConversationStateMachine()