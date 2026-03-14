"""
PHQ-9 Service for scoring and severity calculation.
"""

from app.utils.constants import get_severity_info


class PHQ9Service:
    """Service for PHQ-9 assessment calculations."""
    
    @staticmethod
    def calculate_total_score(responses: list[int]) -> int:
        """
        Calculate total PHQ-9 score from individual responses.
        
        Args:
            responses: List of 9 responses, each 0-3
            
        Returns:
            Total score (0-27)
        """
        if len(responses) != 9:
            raise ValueError("PHQ-9 requires exactly 9 responses")
        
        for i, response in enumerate(responses):
            if response not in [0, 1, 2, 3]:
                raise ValueError(f"Response {i+1} must be 0, 1, 2, or 3")
        
        return sum(responses)
    
    @staticmethod
    def get_severity(score: int) -> str:
        """
        Get severity classification based on PHQ-9 score.
        
        Args:
            score: Total PHQ-9 score (0-27)
            
        Returns:
            Severity string
        """
        return get_severity_info(score)["severity"]
    
    @staticmethod
    def get_risk_level(score: int) -> str:
        """
        Get risk level based on PHQ-9 score.
        
        Args:
            score: Total PHQ-9 score (0-27)
            
        Returns:
            Risk level string
        """
        return get_severity_info(score)["risk_level"]
    
    @staticmethod
    def validate_score(score: int) -> bool:
        """
        Validate PHQ-9 score is within valid range.
        
        Args:
            score: Total PHQ-9 score
            
        Returns:
            True if valid, False otherwise
        """
        return 0 <= score <= 27


# Create singleton instance
phq9_service = PHQ9Service()
