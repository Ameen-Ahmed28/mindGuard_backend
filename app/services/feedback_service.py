"""
Feedback Service for generating AI-powered feedback using Groq API.
"""

import logging
import threading
from typing import Optional

from groq import Groq

from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)


# Feedback prompt template
FEEDBACK_PROMPT_TEMPLATE = """You are a supportive mental health assistant providing feedback based on a PHQ-9 depression screening assessment.

User Assessment Details:
- PHQ-9 Score: {phq_score}/27
- Severity Level: {severity}
- Trend: {trend}
- Detected Emotion from Voice: {emotion}

Guidelines for your response:
1. Be warm, empathetic, and non-judgmental
2. Do NOT provide a medical diagnosis
3. If severity is moderate or higher, gently suggest seeking professional help
4. If showing improvement, acknowledge their progress positively
5. If worsening, encourage them to reach out for support
6. Include 1-2 small, practical self-care suggestions
7. Keep response under 200 words
8. Avoid repetitive phrasing
9. Use a conversational, supportive tone

Generate supportive feedback for this user:"""


class FeedbackService:
    """Service for generating AI-powered feedback using Groq API."""
    
    _instance = None
    _client = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern to avoid creating multiple clients."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the feedback service with Groq client."""
        with self._lock:
            if not self._initialized and self._client is None and settings.groq_api_key:
                self._initialize_client()
                self._initialized = True
    
    def _initialize_client(self):
        """Initialize the Groq API client."""
        try:
            logger.info("Initializing Groq API client")
            self._client = Groq(api_key=settings.groq_api_key)
            logger.info("Groq API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            self._client = None
    
    async def generate_feedback(
        self,
        phq_score: int,
        severity: str,
        trend: str,
        emotion: Optional[str] = None
    ) -> str:
        """
        Generate AI-powered feedback based on assessment results.
        
        Args:
            phq_score: Total PHQ-9 score (0-27)
            severity: Severity classification
            trend: Trend analysis result
            emotion: Detected emotion from voice (optional)
            
        Returns:
            Generated feedback text
        """
        if not self._client:
            logger.warning("Groq client not initialized, using fallback feedback")
            return self._get_fallback_feedback(phq_score, severity, trend)
        
        try:
            # Format the prompt
            prompt = FEEDBACK_PROMPT_TEMPLATE.format(
                phq_score=phq_score,
                severity=severity.replace("_", " ").title(),
                trend=trend.replace("_", " "),
                emotion=emotion or "not detected"
            )
            
            logger.info(f"Generating feedback for PHQ-9 score: {phq_score}")
            
            # Call Groq API
            response = self._client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a compassionate mental health support assistant. Provide supportive, non-diagnostic feedback."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.7,
                top_p=0.9
            )
            
            feedback = response.choices[0].message.content.strip()
            logger.info("Feedback generated successfully")
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            return self._get_fallback_feedback(phq_score, severity, trend)
    
    def _get_fallback_feedback(self, phq_score: int, severity: str, trend: str) -> str:
        """
        Generate fallback feedback when API is unavailable.
        
        Args:
            phq_score: Total PHQ-9 score
            severity: Severity classification
            trend: Trend analysis result
            
        Returns:
            Fallback feedback text
        """
        severity_display = severity.replace("_", " ").title()
        
        # Base feedback based on severity
        if severity == "minimal":
            base = "Your responses suggest minimal symptoms of depression. This is encouraging! Continue taking care of your mental well-being through regular self-care practices."
        elif severity == "mild":
            base = "Your responses suggest mild symptoms. It's good that you're checking in on yourself. Consider incorporating stress-reduction techniques like deep breathing or short walks into your routine."
        elif severity == "moderate":
            base = "Your responses suggest moderate symptoms. While this can feel challenging, support is available. Consider reaching out to a mental health professional who can provide additional guidance and support."
        elif severity == "moderately_severe":
            base = "Your responses suggest moderately severe symptoms. We encourage you to consider speaking with a mental health professional who can provide personalized support. Taking this step shows strength and self-awareness."
        else:  # severe
            base = "Your responses suggest significant symptoms. Please consider reaching out to a mental health professional or a trusted person in your life. Support is available, and you don't have to face this alone."
        
        # Add trend-specific message
        trend_message = ""
        if trend == "significant_improvement":
            trend_message = " It's wonderful to see significant improvement in your scores. Keep up the positive progress!"
        elif trend == "mild_improvement":
            trend_message = " You're showing some improvement, which is encouraging. Continue with what's working for you."
        elif trend == "worsening":
            trend_message = " Your scores have increased since your last assessment. Please consider reaching out for additional support."
        elif trend == "first_assessment":
            trend_message = " This is your first assessment. Regular check-ins can help you track your well-being over time."
        
        return base + trend_message
    
    def is_client_ready(self) -> bool:
        """Check if the Groq client is ready."""
        return self._client is not None


# Create singleton instance
feedback_service = FeedbackService()
