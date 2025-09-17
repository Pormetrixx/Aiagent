"""
Training module for continuous improvement of the AI agent
"""
import logging
import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from ..database.operations import TrainingRepository, ConversationRepository
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class ConversationAnalyzer:
    """Analyzes conversations to extract training insights"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=['der', 'die', 'das', 'und', 'oder', 'aber', 'ist', 'sind', 'haben', 'hat']
        )
    
    def analyze_conversation_quality(self, conversation_turns: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Analyze the quality of a conversation
        
        Args:
            conversation_turns: List of conversation turns
            
        Returns:
            Quality metrics dictionary
        """
        if not conversation_turns:
            return {"overall_quality": 0.0}
        
        metrics = {}
        
        # Basic conversation metrics
        total_turns = len(conversation_turns)
        agent_turns = [turn for turn in conversation_turns if turn.get("speaker") == "agent"]
        customer_turns = [turn for turn in conversation_turns if turn.get("speaker") == "customer"]
        
        metrics["total_turns"] = total_turns
        metrics["agent_turns"] = len(agent_turns)
        metrics["customer_turns"] = len(customer_turns)
        metrics["turn_balance"] = len(customer_turns) / len(agent_turns) if agent_turns else 0.0
        
        # Response time analysis
        response_times = []
        for i in range(1, len(conversation_turns)):
            if conversation_turns[i].get("response_time_ms"):
                response_times.append(conversation_turns[i]["response_time_ms"])
        
        if response_times:
            metrics["avg_response_time"] = np.mean(response_times)
            metrics["max_response_time"] = np.max(response_times)
        
        # Emotion analysis
        emotions = [turn.get("emotion") for turn in conversation_turns if turn.get("emotion")]
        if emotions:
            emotion_counts = {}
            for emotion in emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            metrics["emotion_distribution"] = emotion_counts
            metrics["negative_emotion_ratio"] = (
                emotion_counts.get("angry", 0) + emotion_counts.get("frustrated", 0)
            ) / len(emotions)
        
        # Text analysis
        agent_texts = [turn.get("text_content", "") for turn in agent_turns]
        customer_texts = [turn.get("text_content", "") for turn in customer_turns]
        
        if agent_texts:
            metrics["avg_agent_response_length"] = np.mean([len(text.split()) for text in agent_texts])
        
        if customer_texts:
            metrics["avg_customer_response_length"] = np.mean([len(text.split()) for text in customer_texts])
        
        # Calculate overall quality score
        quality_score = self._calculate_quality_score(metrics)
        metrics["overall_quality"] = quality_score
        
        return metrics
    
    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall conversation quality score"""
        score = 0.5  # Base score
        
        # Good turn balance (customer engagement)
        turn_balance = metrics.get("turn_balance", 0.0)
        if 0.3 <= turn_balance <= 1.5:
            score += 0.2
        
        # Good response times
        avg_response_time = metrics.get("avg_response_time", 5000)
        if avg_response_time < 3000:  # Less than 3 seconds
            score += 0.1
        elif avg_response_time > 10000:  # More than 10 seconds
            score -= 0.1
        
        # Low negative emotions
        negative_ratio = metrics.get("negative_emotion_ratio", 0.0)
        if negative_ratio < 0.2:
            score += 0.2
        elif negative_ratio > 0.5:
            score -= 0.3
        
        # Appropriate conversation length
        total_turns = metrics.get("total_turns", 0)
        if 10 <= total_turns <= 30:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def identify_improvement_opportunities(self, conversation_turns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify specific improvement opportunities in a conversation
        
        Args:
            conversation_turns: List of conversation turns
            
        Returns:
            List of improvement suggestions
        """
        opportunities = []
        
        # Analyze response patterns
        agent_turns = [turn for turn in conversation_turns if turn.get("speaker") == "agent"]
        
        for i, turn in enumerate(agent_turns):
            text = turn.get("text_content", "")
            
            # Check for improvement opportunities
            if len(text.split()) < 5:
                opportunities.append({
                    "type": "response_length",
                    "turn_index": i,
                    "suggestion": "Response too short, consider providing more detailed information",
                    "severity": "medium"
                })
            
            if len(text.split()) > 50:
                opportunities.append({
                    "type": "response_length",
                    "turn_index": i,
                    "suggestion": "Response too long, consider being more concise",
                    "severity": "low"
                })
            
            # Check for repetitive responses
            if i > 0:
                prev_text = agent_turns[i-1].get("text_content", "")
                similarity = self._calculate_text_similarity(text, prev_text)
                if similarity > 0.8:
                    opportunities.append({
                        "type": "repetition",
                        "turn_index": i,
                        "suggestion": "Response too similar to previous response",
                        "severity": "medium"
                    })
        
        return opportunities
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        if not text1 or not text2:
            return 0.0
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity
        except Exception:
            return 0.0


class TrainingDataGenerator:
    """Generates training data from conversation analysis"""
    
    def __init__(self, training_repo: TrainingRepository):
        self.training_repo = training_repo
    
    def generate_training_data_from_conversation(self, conversation_id: int, 
                                               conversation_turns: List[Dict[str, Any]],
                                               outcome: str) -> List[Dict[str, Any]]:
        """
        Generate training data from a conversation
        
        Args:
            conversation_id: Conversation ID
            conversation_turns: List of conversation turns
            outcome: Conversation outcome
            
        Returns:
            List of generated training data entries
        """
        training_data = []
        
        # Generate positive examples from successful conversations
        if outcome in ["appointment_scheduled", "callback_requested"]:
            training_data.extend(self._generate_positive_examples(conversation_id, conversation_turns))
        
        # Generate negative examples from failed conversations
        elif outcome in ["not_interested", "call_failed"]:
            training_data.extend(self._generate_negative_examples(conversation_id, conversation_turns))
        
        # Save training data to database
        for data in training_data:
            self.training_repo.add_training_data(
                conversation_id=conversation_id,
                input_text=data["input_text"],
                expected_response=data["expected_response"],
                actual_response=data["actual_response"],
                feedback_score=data.get("feedback_score"),
                emotion_context=data.get("emotion_context")
            )
        
        return training_data
    
    def _generate_positive_examples(self, conversation_id: int, 
                                  conversation_turns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate positive training examples from successful conversations"""
        positive_examples = []
        
        for i in range(len(conversation_turns) - 1):
            current_turn = conversation_turns[i]
            next_turn = conversation_turns[i + 1]
            
            # Look for customer question followed by good agent response
            if (current_turn.get("speaker") == "customer" and 
                next_turn.get("speaker") == "agent"):
                
                customer_text = current_turn.get("text_content", "")
                agent_response = next_turn.get("text_content", "")
                emotion = current_turn.get("emotion", "neutral")
                
                if len(customer_text.strip()) > 0 and len(agent_response.strip()) > 0:
                    positive_examples.append({
                        "input_text": customer_text,
                        "expected_response": agent_response,
                        "actual_response": agent_response,
                        "feedback_score": 4,  # Good response
                        "emotion_context": emotion
                    })
        
        return positive_examples
    
    def _generate_negative_examples(self, conversation_id: int,
                                  conversation_turns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate negative training examples from failed conversations"""
        negative_examples = []
        
        # Look for patterns that led to conversation failure
        for i in range(len(conversation_turns) - 1):
            current_turn = conversation_turns[i]
            next_turn = conversation_turns[i + 1]
            
            if (current_turn.get("speaker") == "customer" and 
                next_turn.get("speaker") == "agent"):
                
                customer_text = current_turn.get("text_content", "")
                agent_response = next_turn.get("text_content", "")
                emotion = current_turn.get("emotion", "neutral")
                
                # Identify problematic responses
                if emotion in ["angry", "frustrated"] or "nicht interessiert" in customer_text.lower():
                    negative_examples.append({
                        "input_text": customer_text,
                        "expected_response": self._generate_better_response(customer_text, emotion),
                        "actual_response": agent_response,
                        "feedback_score": 2,  # Poor response
                        "emotion_context": emotion
                    })
        
        return negative_examples
    
    def _generate_better_response(self, customer_input: str, emotion: str) -> str:
        """Generate a better response for training purposes"""
        input_lower = customer_input.lower()
        
        if emotion == "angry":
            return "Ich verstehe Ihre Bedenken vollkommen. Lassen Sie mich das gerne für Sie klären."
        elif emotion == "frustrated":
            return "Das kann ich gut nachvollziehen. Wie kann ich Ihnen am besten helfen?"
        elif "nicht interessiert" in input_lower:
            return "Das verstehe ich. Darf ich fragen, was für Sie momentan wichtiger ist?"
        elif "preis" in input_lower or "kosten" in input_lower:
            return "Preis ist natürlich ein wichtiger Faktor. Lassen Sie mich Ihnen den Wert unserer Lösung erklären."
        else:
            return "Vielen Dank für diese Information. Können Sie mir mehr dazu sagen?"


class PerformanceTracker:
    """Tracks and analyzes agent performance over time"""
    
    def __init__(self, conversation_repo: ConversationRepository):
        self.conversation_repo = conversation_repo
    
    def calculate_performance_metrics(self, time_period_days: int = 30) -> Dict[str, Any]:
        """
        Calculate performance metrics for a given time period
        
        Args:
            time_period_days: Number of days to analyze
            
        Returns:
            Performance metrics dictionary
        """
        # This would typically query the database for conversations in the time period
        # For now, we'll return a template structure
        
        metrics = {
            "time_period": f"Last {time_period_days} days",
            "total_calls": 0,
            "successful_calls": 0,
            "success_rate": 0.0,
            "average_call_duration": 0.0,
            "appointments_scheduled": 0,
            "appointment_rate": 0.0,
            "average_response_time": 0.0,
            "customer_satisfaction": 0.0,
            "improvement_areas": []
        }
        
        return metrics
    
    def identify_performance_trends(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Identify performance trends over time
        
        Args:
            metrics_history: Historical performance metrics
            
        Returns:
            Trend analysis results
        """
        if len(metrics_history) < 2:
            return {"trends": "Insufficient data for trend analysis"}
        
        trends = {}
        
        # Analyze success rate trend
        success_rates = [m.get("success_rate", 0.0) for m in metrics_history]
        if len(success_rates) >= 2:
            trend = "improving" if success_rates[-1] > success_rates[0] else "declining"
            trends["success_rate"] = {
                "trend": trend,
                "change": success_rates[-1] - success_rates[0]
            }
        
        # Analyze response time trend
        response_times = [m.get("average_response_time", 0.0) for m in metrics_history]
        if len(response_times) >= 2:
            trend = "improving" if response_times[-1] < response_times[0] else "declining"
            trends["response_time"] = {
                "trend": trend,
                "change": response_times[-1] - response_times[0]
            }
        
        return {"trends": trends}


class ContinuousTrainer:
    """Handles continuous training and improvement of the agent"""
    
    def __init__(self, training_repo: TrainingRepository, conversation_repo: ConversationRepository):
        self.training_repo = training_repo
        self.conversation_repo = conversation_repo
        self.analyzer = ConversationAnalyzer()
        self.data_generator = TrainingDataGenerator(training_repo)
        self.performance_tracker = PerformanceTracker(conversation_repo)
        
        self.min_conversations_for_training = 5
        self.training_enabled = True
    
    def should_trigger_training(self) -> bool:
        """Check if training should be triggered"""
        if not self.training_enabled:
            return False
        
        # Get unused training data count
        unused_data = self.training_repo.get_training_data(used_for_training=False)
        
        return len(unused_data) >= self.min_conversations_for_training
    
    def execute_training_cycle(self) -> Dict[str, Any]:
        """
        Execute a complete training cycle
        
        Returns:
            Training results dictionary
        """
        logger.info("Starting training cycle")
        
        try:
            # Get unused training data
            training_data = self.training_repo.get_training_data(
                limit=100, 
                used_for_training=False
            )
            
            if len(training_data) < self.min_conversations_for_training:
                return {
                    "status": "skipped",
                    "reason": "Insufficient training data",
                    "data_count": len(training_data)
                }
            
            # Analyze training data quality
            quality_metrics = self._analyze_training_data_quality(training_data)
            
            # Simulate training process (in a real implementation, this would
            # train an actual model)
            training_results = self._simulate_training(training_data)
            
            # Mark training data as used
            data_ids = [data.id for data in training_data]
            self.training_repo.mark_training_data_used(data_ids)
            
            logger.info(f"Training cycle completed with {len(training_data)} examples")
            
            return {
                "status": "completed",
                "data_count": len(training_data),
                "quality_metrics": quality_metrics,
                "training_results": training_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in training cycle: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _analyze_training_data_quality(self, training_data: List[Any]) -> Dict[str, Any]:
        """Analyze the quality of training data"""
        if not training_data:
            return {"quality_score": 0.0}
        
        total_score = 0.0
        scored_count = 0
        
        for data in training_data:
            if hasattr(data, 'feedback_score') and data.feedback_score:
                total_score += data.feedback_score
                scored_count += 1
        
        avg_score = total_score / scored_count if scored_count > 0 else 0.0
        
        return {
            "total_examples": len(training_data),
            "scored_examples": scored_count,
            "average_score": avg_score,
            "quality_score": avg_score / 5.0  # Normalize to 0-1
        }
    
    def _simulate_training(self, training_data: List[Any]) -> Dict[str, Any]:
        """Simulate model training process"""
        # In a real implementation, this would involve:
        # 1. Preparing training data
        # 2. Training/fine-tuning a language model
        # 3. Evaluating performance
        # 4. Updating model weights
        
        return {
            "training_loss": 0.25,
            "validation_accuracy": 0.85,
            "epochs_completed": 10,
            "model_improvements": [
                "Better handling of price objections",
                "Improved emotional adaptation",
                "More natural conversation flow"
            ]
        }
    
    def generate_improvement_report(self) -> Dict[str, Any]:
        """Generate a comprehensive improvement report"""
        try:
            # Get performance metrics
            performance_metrics = self.performance_tracker.calculate_performance_metrics()
            
            # Get recent training results
            # This would typically query recent training cycles from a database
            
            report = {
                "generated_at": datetime.utcnow().isoformat(),
                "performance_metrics": performance_metrics,
                "training_status": {
                    "enabled": self.training_enabled,
                    "ready_for_training": self.should_trigger_training()
                },
                "recommendations": self._generate_recommendations(performance_metrics)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating improvement report: {e}")
            return {
                "generated_at": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def _generate_recommendations(self, performance_metrics: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on performance"""
        recommendations = []
        
        success_rate = performance_metrics.get("success_rate", 0.0)
        if success_rate < 0.3:
            recommendations.append("Consider improving opening scripts and objection handling")
        
        response_time = performance_metrics.get("average_response_time", 0.0)
        if response_time > 5000:  # 5 seconds
            recommendations.append("Work on reducing response times for better conversation flow")
        
        appointment_rate = performance_metrics.get("appointment_rate", 0.0)
        if appointment_rate < 0.2:
            recommendations.append("Focus on improving closing techniques and appointment scheduling")
        
        if not recommendations:
            recommendations.append("Performance is good, continue current practices")
        
        return recommendations


def create_continuous_trainer(training_repo: TrainingRepository, 
                            conversation_repo: ConversationRepository) -> ContinuousTrainer:
    """Factory function to create continuous trainer"""
    return ContinuousTrainer(training_repo, conversation_repo)