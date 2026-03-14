"""
Constants and configuration for the Mental Health Monitoring System.
Contains PHQ-9 questions, severity mappings, and other constants.
"""

# PHQ-9 Questions with response options
PHQ9_QUESTIONS = [
    {
        "id": 1,
        "question": "Over the last 2 weeks, how often have you been bothered by any of the following problems? Little interest or pleasure in doing things",
        "options": [
            {"value": 0, "label": "Not at all"},
            {"value": 1, "label": "Several days"},
            {"value": 2, "label": "More than half the days"},
            {"value": 3, "label": "Nearly every day"}
        ]
    },
    {
        "id": 2,
        "question": "Feeling down, depressed, or hopeless",
        "options": [
            {"value": 0, "label": "Not at all"},
            {"value": 1, "label": "Several days"},
            {"value": 2, "label": "More than half the days"},
            {"value": 3, "label": "Nearly every day"}
        ]
    },
    {
        "id": 3,
        "question": "Trouble falling or staying asleep, or sleeping too much",
        "options": [
            {"value": 0, "label": "Not at all"},
            {"value": 1, "label": "Several days"},
            {"value": 2, "label": "More than half the days"},
            {"value": 3, "label": "Nearly every day"}
        ]
    },
    {
        "id": 4,
        "question": "Feeling tired or having little energy",
        "options": [
            {"value": 0, "label": "Not at all"},
            {"value": 1, "label": "Several days"},
            {"value": 2, "label": "More than half the days"},
            {"value": 3, "label": "Nearly every day"}
        ]
    },
    {
        "id": 5,
        "question": "Poor appetite or overeating",
        "options": [
            {"value": 0, "label": "Not at all"},
            {"value": 1, "label": "Several days"},
            {"value": 2, "label": "More than half the days"},
            {"value": 3, "label": "Nearly every day"}
        ]
    },
    {
        "id": 6,
        "question": "Feeling bad about yourself — or that you are a failure or have let yourself or your family down",
        "options": [
            {"value": 0, "label": "Not at all"},
            {"value": 1, "label": "Several days"},
            {"value": 2, "label": "More than half the days"},
            {"value": 3, "label": "Nearly every day"}
        ]
    },
    {
        "id": 7,
        "question": "Trouble concentrating on things, such as reading the newspaper or watching television",
        "options": [
            {"value": 0, "label": "Not at all"},
            {"value": 1, "label": "Several days"},
            {"value": 2, "label": "More than half the days"},
            {"value": 3, "label": "Nearly every day"}
        ]
    },
    {
        "id": 8,
        "question": "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual",
        "options": [
            {"value": 0, "label": "Not at all"},
            {"value": 1, "label": "Several days"},
            {"value": 2, "label": "More than half the days"},
            {"value": 3, "label": "Nearly every day"}
        ]
    },
    {
        "id": 9,
        "question": "Thoughts that you would be better off dead or of hurting yourself in some way",
        "options": [
            {"value": 0, "label": "Not at all"},
            {"value": 1, "label": "Several days"},
            {"value": 2, "label": "More than half the days"},
            {"value": 3, "label": "Nearly every day"}
        ]
    }
]

# Severity mapping based on PHQ-9 score
SEVERITY_MAPPING = {
    (0, 4): {
        "severity": "minimal",
        "risk_level": "low",
        "description": "Minimal or no depressive symptoms"
    },
    (5, 9): {
        "severity": "mild",
        "risk_level": "low",
        "description": "Mild depressive symptoms"
    },
    (10, 14): {
        "severity": "moderate",
        "risk_level": "moderate",
        "description": "Moderate depressive symptoms"
    },
    (15, 19): {
        "severity": "moderately_severe",
        "risk_level": "moderate",
        "description": "Moderately severe depressive symptoms"
    },
    (20, 27): {
        "severity": "severe",
        "risk_level": "high",
        "description": "Severe depressive symptoms"
    }
}

# Trend analysis thresholds
TREND_THRESHOLDS = {
    "significant_improvement": 5,  # Score decreased by 5 or more
    "mild_improvement": 1,  # Score decreased by 1-4
}

# Crisis helpline information
CRISIS_INFO = {
    "india": {
        "name": "KIRAN Mental Health Helpline",
        "number": "1800-599-0019",
        "message": "If you are in India, contact KIRAN Mental Health Helpline: 1800-599-0019"
    }
}

# Supported emotions from the HuggingFace model
SUPPORTED_EMOTIONS = [
    "angry",
    "disgust",
    "fear",
    "happy",
    "neutral",
    "sad",
    "surprise"
]

# Voice recording settings
VOICE_RECORDING = {
    "max_duration_seconds": 15,
    "min_duration_seconds": 3,
    "sample_rate": 16000,
    "supported_formats": ["webm", "wav", "mp3", "ogg"]
}

# Paragraph for voice recording
VOICE_RECORDING_PARAGRAPH = """
Please read the following paragraph aloud:
'I am taking a moment to check in with myself today. It is important to acknowledge how I am feeling, 
whatever those feelings may be. Each day brings new opportunities for growth and self-care. 
I am taking this step towards better understanding my mental health and well-being.'
"""


def get_severity_info(score: int) -> dict:
    """
    Get severity information based on PHQ-9 score.
    
    Args:
        score: PHQ-9 total score (0-27)
        
    Returns:
        Dictionary with severity, risk_level, and description
    """
    for (min_score, max_score), info in SEVERITY_MAPPING.items():
        if min_score <= score <= max_score:
            return info
    return SEVERITY_MAPPING[(0, 4)]  # Default to minimal


def calculate_trend(current_score: int, previous_score: int | None) -> str:
    """
    Calculate trend based on current and previous PHQ-9 scores.
    
    Args:
        current_score: Current PHQ-9 score
        previous_score: Previous PHQ-9 score (None if first assessment)
        
    Returns:
        Trend string: first_assessment, significant_improvement, 
                     mild_improvement, no_change, or worsening
    """
    if previous_score is None:
        return "first_assessment"
    
    difference = previous_score - current_score
    
    if difference >= TREND_THRESHOLDS["significant_improvement"]:
        return "significant_improvement"
    elif difference >= TREND_THRESHOLDS["mild_improvement"]:
        return "mild_improvement"
    elif difference == 0:
        return "no_change"
    else:
        return "worsening"


def get_crisis_message(risk_level: str) -> str | None:
    """
    Get crisis helpline message if risk level is high.
    
    Args:
        risk_level: Risk level classification
        
    Returns:
        Crisis message if high risk, None otherwise
    """
    if risk_level == "high":
        return CRISIS_INFO["india"]["message"]
    return None
