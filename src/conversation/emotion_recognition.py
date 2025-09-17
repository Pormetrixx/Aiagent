"""
Emotion recognition module for analyzing customer emotions
"""
import logging
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
import cv2
from pathlib import Path

logger = logging.getLogger(__name__)


class TextEmotionAnalyzer:
    """Analyzes emotions from text using various methods"""
    
    def __init__(self):
        self.emotion_keywords = {
            "angry": [
                "wütend", "ärgerlich", "sauer", "verärgert", "böse", "zornig",
                "empört", "aufgebracht", "gereizt", "schlecht", "schlimm"
            ],
            "frustrated": [
                "frustriert", "genervt", "gestresst", "müde", "erschöpft",
                "enttäuscht", "unzufrieden", "kompliziert", "schwierig"
            ],
            "confused": [
                "verwirrt", "durcheinander", "verstehe nicht", "unklar",
                "wie bitte", "was meinen sie", "erklären", "verstehen"
            ],
            "interested": [
                "interessant", "spannend", "toll", "gut", "großartig",
                "perfekt", "ja", "gerne", "mehr", "details", "erzählen"
            ],
            "happy": [
                "freut mich", "schön", "prima", "super", "wunderbar",
                "ausgezeichnet", "fantastisch", "begeistert"
            ],
            "sad": [
                "traurig", "schade", "bedauerlich", "schlimm", "tut mir leid",
                "leider", "unglücklich"
            ],
            "anxious": [
                "sorge", "angst", "bedenken", "unsicher", "zweifel",
                "befürchte", "nervös", "unruhig"
            ],
            "neutral": [
                "okay", "in ordnung", "verstehe", "gut", "danke", "bitte"
            ]
        }
        
        # Initialize sentiment analyzer if available
        self.sentiment_analyzer = None
        self._init_sentiment_analyzer()
    
    def _init_sentiment_analyzer(self):
        """Initialize sentiment analyzer if libraries are available"""
        try:
            from transformers import pipeline
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
                device=-1  # Use CPU
            )
            logger.info("Sentiment analyzer initialized successfully")
        except ImportError:
            logger.warning("Transformers not available for sentiment analysis")
        except Exception as e:
            logger.warning(f"Could not initialize sentiment analyzer: {e}")
    
    def analyze_text_emotion(self, text: str) -> Dict[str, Any]:
        """
        Analyze emotion from text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with emotion analysis results
        """
        text_lower = text.lower()
        
        # Keyword-based emotion detection
        emotion_scores = {}
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score / len(keywords)
        
        # Determine primary emotion
        primary_emotion = "neutral"
        max_score = 0.0
        
        if emotion_scores:
            primary_emotion = max(emotion_scores.keys(), key=lambda k: emotion_scores[k])
            max_score = emotion_scores[primary_emotion]
        
        # Get sentiment if analyzer is available
        sentiment_result = None
        if self.sentiment_analyzer:
            try:
                sentiment_result = self.sentiment_analyzer(text)[0]
            except Exception as e:
                logger.error(f"Error in sentiment analysis: {e}")
        
        return {
            "primary_emotion": primary_emotion,
            "confidence": max_score,
            "emotion_scores": emotion_scores,
            "sentiment": sentiment_result,
            "text_features": self._extract_text_features(text)
        }
    
    def _extract_text_features(self, text: str) -> Dict[str, Any]:
        """Extract additional features from text"""
        return {
            "length": len(text),
            "word_count": len(text.split()),
            "exclamation_marks": text.count("!"),
            "question_marks": text.count("?"),
            "uppercase_ratio": sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            "has_profanity": self._check_profanity(text.lower())
        }
    
    def _check_profanity(self, text: str) -> bool:
        """Check for profanity in text"""
        profanity_words = [
            "scheiße", "verdammt", "mist", "quatsch", "blödsinn",
            "idiot", "dumm", "verrückt", "wahnsinn"
        ]
        return any(word in text for word in profanity_words)


class AudioEmotionAnalyzer:
    """Analyzes emotions from audio features"""
    
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load emotion recognition model if available"""
        try:
            # Try to load a pre-trained emotion recognition model
            # This would typically be a deep learning model trained on emotional speech
            logger.info("Audio emotion recognition model initialized")
        except Exception as e:
            logger.warning(f"Could not load audio emotion model: {e}")
    
    def analyze_audio_emotion(self, audio_path: str) -> Dict[str, Any]:
        """
        Analyze emotion from audio file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with emotion analysis results
        """
        try:
            # Extract audio features
            features = self._extract_audio_features(audio_path)
            
            # Analyze using simple heuristics (can be enhanced with ML models)
            emotion_result = self._analyze_audio_features(features)
            
            return {
                "primary_emotion": emotion_result["emotion"],
                "confidence": emotion_result["confidence"],
                "audio_features": features,
                "analysis_method": "feature_based"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing audio emotion: {e}")
            return {
                "primary_emotion": "neutral",
                "confidence": 0.0,
                "audio_features": {},
                "analysis_method": "fallback"
            }
    
    def _extract_audio_features(self, audio_path: str) -> Dict[str, float]:
        """Extract features from audio file"""
        try:
            import librosa
            
            # Load audio file
            y, sr = librosa.load(audio_path, sr=None)
            
            # Extract features
            features = {
                "duration": len(y) / sr,
                "rms_energy": float(np.mean(librosa.feature.rms(y=y))),
                "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(y))),
                "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
                "spectral_rolloff": float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))),
                "tempo": float(librosa.beat.tempo(y=y, sr=sr)[0])
            }
            
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            for i in range(13):
                features[f"mfcc_{i}"] = float(np.mean(mfccs[i]))
            
            return features
            
        except ImportError:
            logger.warning("librosa not available for audio feature extraction")
            return {}
        except Exception as e:
            logger.error(f"Error extracting audio features: {e}")
            return {}
    
    def _analyze_audio_features(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Analyze emotion based on audio features"""
        if not features:
            return {"emotion": "neutral", "confidence": 0.0}
        
        # Simple heuristic-based emotion detection
        # These thresholds would typically be learned from training data
        
        energy = features.get("rms_energy", 0.0)
        tempo = features.get("tempo", 120.0)
        spectral_centroid = features.get("spectral_centroid", 1000.0)
        
        # High energy + fast tempo = excited/angry
        if energy > 0.1 and tempo > 140:
            if spectral_centroid > 2000:
                return {"emotion": "angry", "confidence": 0.7}
            else:
                return {"emotion": "excited", "confidence": 0.6}
        
        # Low energy + slow tempo = sad
        elif energy < 0.05 and tempo < 100:
            return {"emotion": "sad", "confidence": 0.6}
        
        # Moderate values = neutral
        else:
            return {"emotion": "neutral", "confidence": 0.5}


class FacialEmotionAnalyzer:
    """Analyzes emotions from facial expressions (if video is available)"""
    
    def __init__(self):
        self.fer_detector = None
        self._init_fer_detector()
    
    def _init_fer_detector(self):
        """Initialize facial emotion recognition detector"""
        try:
            from fer import FER
            self.fer_detector = FER(mtcnn=True)
            logger.info("Facial emotion recognition initialized")
        except ImportError:
            logger.warning("FER library not available for facial emotion recognition")
        except Exception as e:
            logger.warning(f"Could not initialize FER detector: {e}")
    
    def analyze_facial_emotion(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze emotion from facial image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with emotion analysis results
        """
        if not self.fer_detector:
            return {
                "primary_emotion": "neutral",
                "confidence": 0.0,
                "emotion_scores": {},
                "analysis_method": "unavailable"
            }
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Detect emotions
            result = self.fer_detector.detect_emotions(image)
            
            if result:
                # Get the first detected face
                emotions = result[0]["emotions"]
                
                # Find primary emotion
                primary_emotion = max(emotions.keys(), key=lambda k: emotions[k])
                confidence = emotions[primary_emotion]
                
                return {
                    "primary_emotion": primary_emotion,
                    "confidence": confidence,
                    "emotion_scores": emotions,
                    "analysis_method": "facial_recognition"
                }
            else:
                return {
                    "primary_emotion": "neutral",
                    "confidence": 0.0,
                    "emotion_scores": {},
                    "analysis_method": "no_face_detected"
                }
                
        except Exception as e:
            logger.error(f"Error analyzing facial emotion: {e}")
            return {
                "primary_emotion": "neutral",
                "confidence": 0.0,
                "emotion_scores": {},
                "analysis_method": "error"
            }


class EmotionRecognitionSystem:
    """Unified emotion recognition system combining multiple modalities"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.confidence_threshold = self.config.get("confidence_threshold", 0.7)
        self.adaptation_strength = self.config.get("adaptation_strength", 0.3)
        
        # Initialize analyzers
        self.text_analyzer = TextEmotionAnalyzer()
        self.audio_analyzer = AudioEmotionAnalyzer()
        self.facial_analyzer = FacialEmotionAnalyzer()
        
        # Emotion history for smoothing
        self.emotion_history: List[Dict[str, Any]] = []
        self.max_history = 5
    
    def analyze_multimodal_emotion(self, text: Optional[str] = None,
                                 audio_path: Optional[str] = None,
                                 image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze emotion using multiple modalities
        
        Args:
            text: Text input
            audio_path: Path to audio file
            image_path: Path to image file
            
        Returns:
            Combined emotion analysis results
        """
        results = {}
        
        # Analyze text emotion
        if text:
            results["text"] = self.text_analyzer.analyze_text_emotion(text)
        
        # Analyze audio emotion
        if audio_path:
            results["audio"] = self.audio_analyzer.analyze_audio_emotion(audio_path)
        
        # Analyze facial emotion
        if image_path:
            results["facial"] = self.facial_analyzer.analyze_facial_emotion(image_path)
        
        # Combine results
        combined_result = self._combine_emotion_results(results)
        
        # Add to history and smooth
        self.emotion_history.append(combined_result)
        if len(self.emotion_history) > self.max_history:
            self.emotion_history.pop(0)
        
        smoothed_result = self._smooth_emotions()
        
        return {
            "current_emotion": combined_result,
            "smoothed_emotion": smoothed_result,
            "modality_results": results,
            "confidence": smoothed_result["confidence"],
            "adaptation_needed": smoothed_result["confidence"] > self.confidence_threshold
        }
    
    def _combine_emotion_results(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Combine emotion results from different modalities"""
        if not results:
            return {"primary_emotion": "neutral", "confidence": 0.0}
        
        # Weight different modalities
        weights = {
            "text": 0.5,
            "audio": 0.3,
            "facial": 0.2
        }
        
        # Collect all emotions with their weighted confidences
        emotion_votes = {}
        total_weight = 0.0
        
        for modality, result in results.items():
            if modality in weights:
                weight = weights[modality]
                emotion = result["primary_emotion"]
                confidence = result["confidence"]
                
                if emotion not in emotion_votes:
                    emotion_votes[emotion] = 0.0
                
                emotion_votes[emotion] += weight * confidence
                total_weight += weight
        
        # Normalize and find primary emotion
        if emotion_votes and total_weight > 0:
            for emotion in emotion_votes:
                emotion_votes[emotion] /= total_weight
            
            primary_emotion = max(emotion_votes.keys(), key=lambda k: emotion_votes[k])
            confidence = emotion_votes[primary_emotion]
        else:
            primary_emotion = "neutral"
            confidence = 0.0
        
        return {
            "primary_emotion": primary_emotion,
            "confidence": confidence,
            "emotion_votes": emotion_votes
        }
    
    def _smooth_emotions(self) -> Dict[str, Any]:
        """Smooth emotions over time to reduce noise"""
        if not self.emotion_history:
            return {"primary_emotion": "neutral", "confidence": 0.0}
        
        # Weight recent emotions more heavily
        weights = [0.4, 0.3, 0.2, 0.1] if len(self.emotion_history) >= 4 else [1.0]
        
        emotion_scores = {}
        total_weight = 0.0
        
        for i, emotion_data in enumerate(reversed(self.emotion_history)):
            weight = weights[min(i, len(weights) - 1)]
            emotion = emotion_data["primary_emotion"]
            confidence = emotion_data["confidence"]
            
            if emotion not in emotion_scores:
                emotion_scores[emotion] = 0.0
            
            emotion_scores[emotion] += weight * confidence
            total_weight += weight
        
        # Normalize
        if emotion_scores and total_weight > 0:
            for emotion in emotion_scores:
                emotion_scores[emotion] /= total_weight
            
            primary_emotion = max(emotion_scores.keys(), key=lambda k: emotion_scores[k])
            confidence = emotion_scores[primary_emotion]
        else:
            primary_emotion = "neutral"
            confidence = 0.0
        
        return {
            "primary_emotion": primary_emotion,
            "confidence": confidence,
            "emotion_scores": emotion_scores
        }
    
    def is_available(self) -> Dict[str, bool]:
        """Check availability of different emotion recognition modalities"""
        return {
            "text": True,  # Always available
            "audio": hasattr(self.audio_analyzer, 'model'),
            "facial": self.facial_analyzer.fer_detector is not None
        }


def create_emotion_recognition_system(config: Optional[Dict[str, Any]] = None) -> EmotionRecognitionSystem:
    """Factory function to create emotion recognition system"""
    return EmotionRecognitionSystem(config)