"""
Risk Service for determining risk levels based on PHQ-9 scores.
"""

from app.utils.constants import get_severity_info, get_crisis_message


class RiskService:
    """Service for risk level determination."""
    
    @staticmethod
    def get_risk_level(phq_score: int) -> str:
        """
        Determine risk level based on PHQ-9 score.
        
        Risk levels:
        - phq_score >= 20 → high risk
        - phq_score >= 10 → moderate risk
        - else → low risk
        
        Args:
            phq_score: Total PHQ-9 score (0-27)
            
        Returns:
            Risk level string
        """
        return get_severity_info(phq_score)["risk_level"]
    
    @staticmethod
    def is_high_risk(phq_score: int) -> bool:
        """
        Check if the score indicates high risk.
        
        Args:
            phq_score: Total PHQ-9 score
            
        Returns:
            True if high risk, False otherwise
        """
        return phq_score >= 20
    
    @staticmethod
    def get_crisis_info(phq_score: int) -> dict:
        """
        Get crisis information if applicable.
        
        Args:
            phq_score: Total PHQ-9 score
            
        Returns:
            Dictionary with crisis message if high risk, empty otherwise
        """
        risk_level = RiskService.get_risk_level(phq_score)
        crisis_message = get_crisis_message(risk_level)
        
        if crisis_message:
            return {
                "is_crisis": True,
                "message": crisis_message,
                "risk_level": risk_level
            }
        return {
            "is_crisis": False,
            "message": None,
            "risk_level": risk_level
        }


# Create singleton instance
risk_service = RiskService()
