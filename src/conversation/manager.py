"""
Conversation manager for handling call flow and response generation
"""
import logging
import re
import random
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from .state_machine import ConversationStateMachine, ConversationState
from ..database.operations import ConversationRepository, FAQRepository, ScriptRepository

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """Generates appropriate responses based on conversation context"""
    
    def __init__(self, faq_repo: FAQRepository, script_repo: ScriptRepository):
        self.faq_repo = faq_repo
        self.script_repo = script_repo
    
    def generate_response(self, context: Dict[str, Any], customer_input: str, 
                         emotion: Optional[str] = None) -> str:
        """
        Generate appropriate response based on context and input
        
        Args:
            context: Conversation context
            customer_input: Customer's input text
            emotion: Detected customer emotion
            
        Returns:
            Generated response text
        """
        # First try to find FAQ match
        faq_response = self._find_faq_response(customer_input)
        if faq_response:
            return self._adapt_response_to_emotion(faq_response, emotion)
        
        # Then try to get script response
        script_type = context.get("current_script_type", "general")
        script_response = self._get_script_response(script_type, context)
        if script_response:
            return self._adapt_response_to_emotion(script_response, emotion)
        
        # Generate fallback response
        return self._generate_fallback_response(customer_input, emotion)
    
    def _find_faq_response(self, customer_input: str) -> Optional[str]:
        """Find matching FAQ response for customer input"""
        try:
            faq_entries = self.faq_repo.search_faq(customer_input, limit=1)
            if faq_entries:
                faq = faq_entries[0]
                # Increment usage count
                self.faq_repo.increment_faq_usage(faq.id)
                return faq.answer
        except Exception as e:
            logger.error(f"Error searching FAQ: {e}")
        
        return None
    
    def _get_script_response(self, script_type: str, context: Dict[str, Any]) -> Optional[str]:
        """Get script response for current conversation state"""
        try:
            script = self.script_repo.get_script_by_type(script_type)
            if script:
                # Replace variables in script content
                response = self._replace_script_variables(script.content, script.variables, context)
                return response
        except Exception as e:
            logger.error(f"Error getting script response: {e}")
        
        return None
    
    def _replace_script_variables(self, content: str, variables: Dict[str, Any], 
                                context: Dict[str, Any]) -> str:
        """Replace variables in script content"""
        if not variables:
            return content
        
        # Merge default variables with context
        all_variables = {**variables, **context}
        
        # Replace variables using format strings
        try:
            return content.format(**all_variables)
        except KeyError as e:
            logger.warning(f"Missing variable in script: {e}")
            return content
        except Exception as e:
            logger.error(f"Error replacing script variables: {e}")
            return content
    
    def _adapt_response_to_emotion(self, response: str, emotion: Optional[str]) -> str:
        """Adapt response based on detected customer emotion"""
        if not emotion:
            return response
        
        emotion_adaptations = {
            "angry": {
                "prefix": "Ich verstehe Ihre Bedenken. ",
                "tone": "calm"
            },
            "frustrated": {
                "prefix": "Ich kann verstehen, dass das frustrierend ist. ",
                "tone": "empathetic"
            },
            "confused": {
                "prefix": "Lassen Sie mich das gerne genauer erklären. ",
                "tone": "helpful"
            },
            "interested": {
                "prefix": "",
                "tone": "enthusiastic"
            },
            "neutral": {
                "prefix": "",
                "tone": "professional"
            }
        }
        
        adaptation = emotion_adaptations.get(emotion, emotion_adaptations["neutral"])
        
        # Add appropriate prefix
        adapted_response = adaptation["prefix"] + response
        
        # Modify tone if needed
        if adaptation["tone"] == "calm":
            adapted_response = self._make_response_calmer(adapted_response)
        elif adaptation["tone"] == "empathetic":
            adapted_response = self._make_response_empathetic(adapted_response)
        elif adaptation["tone"] == "enthusiastic":
            adapted_response = self._make_response_enthusiastic(adapted_response)
        
        return adapted_response
    
    def _make_response_calmer(self, response: str) -> str:
        """Make response calmer and more reassuring"""
        calming_phrases = [
            "Ganz ruhig,",
            "Kein Problem,",
            "Das verstehe ich gut,",
            "Das ist völlig verständlich,"
        ]
        
        # Add calming phrase occasionally
        if random.random() < 0.3:
            phrase = random.choice(calming_phrases)
            response = phrase + " " + response.lower()
        
        return response
    
    def _make_response_empathetic(self, response: str) -> str:
        """Make response more empathetic"""
        empathetic_phrases = [
            "Das kann ich gut nachvollziehen.",
            "Ihre Bedenken sind berechtigt.",
            "Das ist ein wichtiger Punkt.",
            "Ich verstehe Ihre Situation."
        ]
        
        # Add empathetic phrase
        if random.random() < 0.4:
            phrase = random.choice(empathetic_phrases)
            response = phrase + " " + response
        
        return response
    
    def _make_response_enthusiastic(self, response: str) -> str:
        """Make response more enthusiastic"""
        enthusiastic_endings = [
            "Das ist großartig!",
            "Perfekt!",
            "Wunderbar!",
            "Das freut mich sehr!"
        ]
        
        # Add enthusiastic ending occasionally
        if random.random() < 0.3:
            ending = random.choice(enthusiastic_endings)
            response = response + " " + ending
        
        return response
    
    def _generate_fallback_response(self, customer_input: str, emotion: Optional[str]) -> str:
        """Generate fallback response when no FAQ or script match is found"""
        fallback_responses = [
            "Das ist ein interessanter Punkt. Können Sie mir mehr dazu sagen?",
            "Ich verstehe. Lassen Sie mich das für Sie klären.",
            "Das ist eine gute Frage. Darf ich Ihnen dazu etwas erläutern?",
            "Vielen Dank für diese Information. Wie kann ich Ihnen am besten helfen?",
            "Das kann ich gut nachvollziehen. Was wäre für Sie am wichtigsten?"
        ]
        
        base_response = random.choice(fallback_responses)
        return self._adapt_response_to_emotion(base_response, emotion)


class ConversationManager:
    """Manages the complete conversation flow"""
    
    def __init__(self, conversation_repo: ConversationRepository, 
                 faq_repo: FAQRepository, script_repo: ScriptRepository):
        self.conversation_repo = conversation_repo
        self.faq_repo = faq_repo
        self.script_repo = script_repo
        self.response_generator = ResponseGenerator(faq_repo, script_repo)
        self.active_conversations: Dict[str, ConversationStateMachine] = {}
    
    def start_conversation(self, call_id: str, customer_phone: str, 
                          customer_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new conversation
        
        Args:
            call_id: Unique call identifier
            customer_phone: Customer phone number
            customer_name: Customer name (optional)
            
        Returns:
            Initial conversation response
        """
        try:
            # Create conversation record in database
            conversation = self.conversation_repo.create_conversation(
                call_id=call_id,
                customer_phone=customer_phone,
                customer_name=customer_name
            )
            
            # Create state machine for this conversation
            state_machine = ConversationStateMachine()
            state_machine.start_conversation(customer_phone, customer_name)
            
            # Store active conversation
            self.active_conversations[call_id] = state_machine
            
            # Generate opening response
            opening_script = self.script_repo.get_script_by_type("opening")
            if opening_script:
                response_text = self._replace_script_variables(
                    opening_script.content,
                    opening_script.variables or {},
                    {
                        "customer_name": customer_name or "dort",
                        "agent_name": "Sarah",
                        "company_name": "Digital Solutions"
                    }
                )
            else:
                response_text = f"Guten Tag{', ' + customer_name if customer_name else ''}! Mein Name ist Sarah von Digital Solutions."
            
            # Add agent turn to conversation
            self.conversation_repo.add_conversation_turn(
                conversation_id=conversation.id,
                speaker="agent",
                text_content=response_text
            )
            
            return {
                "conversation_id": conversation.id,
                "call_id": call_id,
                "response": response_text,
                "state": state_machine.state,
                "script_type": state_machine.get_current_script_type()
            }
            
        except Exception as e:
            logger.error(f"Error starting conversation {call_id}: {e}")
            raise
    
    def process_customer_input(self, call_id: str, customer_input: str, 
                             emotion: Optional[str] = None, 
                             confidence_score: Optional[float] = None) -> Dict[str, Any]:
        """
        Process customer input and generate response
        
        Args:
            call_id: Call identifier
            customer_input: Customer's input text
            emotion: Detected emotion
            confidence_score: STT confidence score
            
        Returns:
            Agent response and conversation state
        """
        try:
            # Get active conversation
            if call_id not in self.active_conversations:
                raise ValueError(f"No active conversation found for call_id: {call_id}")
            
            state_machine = self.active_conversations[call_id]
            conversation = self.conversation_repo.get_conversation(call_id)
            
            if not conversation:
                raise ValueError(f"No conversation record found for call_id: {call_id}")
            
            # Add customer turn to conversation
            customer_turn = self.conversation_repo.add_conversation_turn(
                conversation_id=conversation.id,
                speaker="customer",
                text_content=customer_input,
                emotion=emotion,
                confidence_score=confidence_score
            )
            
            # Process input through state machine
            transition_result = state_machine.process_customer_input(customer_input, emotion)
            
            # Generate appropriate response
            context = {
                "customer_name": state_machine.context.customer_name,
                "customer_phone": state_machine.context.customer_phone,
                "current_script_type": state_machine.get_current_script_type(),
                "conversation_history": state_machine.context.conversation_history,
                "objections_count": state_machine.context.objections_count,
                "agent_name": "Sarah",
                "company_name": "Digital Solutions"
            }
            
            response_text = self.response_generator.generate_response(
                context, customer_input, emotion
            )
            
            # Add agent response to conversation
            agent_turn = self.conversation_repo.add_conversation_turn(
                conversation_id=conversation.id,
                speaker="agent",
                text_content=response_text
            )
            
            # Check if conversation should end
            should_end = state_machine.is_conversation_ended()
            
            if should_end:
                # End conversation and clean up
                outcome = state_machine.get_conversation_outcome()
                self.end_conversation(call_id, outcome)
            
            return {
                "conversation_id": conversation.id,
                "call_id": call_id,
                "response": response_text,
                "state": state_machine.state,
                "script_type": state_machine.get_current_script_type(),
                "transition_result": transition_result,
                "should_end": should_end,
                "outcome": state_machine.get_conversation_outcome() if should_end else None
            }
            
        except Exception as e:
            logger.error(f"Error processing customer input for {call_id}: {e}")
            raise
    
    def end_conversation(self, call_id: str, outcome: str, 
                        emotion_score: Optional[float] = None,
                        sentiment_score: Optional[float] = None):
        """
        End a conversation
        
        Args:
            call_id: Call identifier
            outcome: Conversation outcome
            emotion_score: Overall emotion score
            sentiment_score: Overall sentiment score
        """
        try:
            # Get conversation from database
            conversation = self.conversation_repo.get_conversation(call_id)
            if conversation:
                self.conversation_repo.end_conversation(
                    conversation_id=conversation.id,
                    outcome=outcome,
                    emotion_score=emotion_score,
                    sentiment_score=sentiment_score
                )
            
            # Remove from active conversations
            if call_id in self.active_conversations:
                del self.active_conversations[call_id]
            
            logger.info(f"Conversation {call_id} ended with outcome: {outcome}")
            
        except Exception as e:
            logger.error(f"Error ending conversation {call_id}: {e}")
            raise
    
    def get_conversation_state(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get current conversation state"""
        if call_id not in self.active_conversations:
            return None
        
        state_machine = self.active_conversations[call_id]
        conversation = self.conversation_repo.get_conversation(call_id)
        
        return {
            "call_id": call_id,
            "conversation_id": conversation.id if conversation else None,
            "state": state_machine.state,
            "customer_name": state_machine.context.customer_name,
            "customer_phone": state_machine.context.customer_phone,
            "duration": state_machine.context.get_conversation_duration(),
            "turns_count": len(state_machine.context.conversation_history),
            "objections_count": state_machine.context.objections_count,
            "script_type": state_machine.get_current_script_type()
        }
    
    def _replace_script_variables(self, content: str, variables: Dict[str, Any], 
                                context: Dict[str, Any]) -> str:
        """Helper method to replace script variables"""
        if not variables:
            variables = {}
        
        # Merge variables with context
        all_variables = {**variables, **context}
        
        try:
            return content.format(**all_variables)
        except KeyError as e:
            logger.warning(f"Missing variable in script: {e}")
            return content
        except Exception as e:
            logger.error(f"Error replacing script variables: {e}")
            return content
    
    def get_active_conversations_count(self) -> int:
        """Get number of active conversations"""
        return len(self.active_conversations)
    
    def cleanup_inactive_conversations(self, max_duration_minutes: int = 30):
        """Clean up conversations that have been inactive for too long"""
        current_time = datetime.utcnow()
        to_remove = []
        
        for call_id, state_machine in self.active_conversations.items():
            if state_machine.context.call_start_time:
                duration = (current_time - state_machine.context.call_start_time).total_seconds()
                if duration > max_duration_minutes * 60:
                    to_remove.append(call_id)
        
        for call_id in to_remove:
            logger.info(f"Cleaning up inactive conversation: {call_id}")
            self.end_conversation(call_id, "timeout")


def create_conversation_manager(conversation_repo: ConversationRepository,
                              faq_repo: FAQRepository,
                              script_repo: ScriptRepository) -> ConversationManager:
    """Factory function to create conversation manager"""
    return ConversationManager(conversation_repo, faq_repo, script_repo)