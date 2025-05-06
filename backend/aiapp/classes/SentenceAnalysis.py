from pydantic import BaseModel, Field

class SentenceAnalysis(BaseModel):
    command: str
    followup: str
    time_duration: int = Field(
        description=(
            "Time duration in hours. "
            "Convert any duration expressed in other units (e.g., days, weeks, months etc) to hours. "
            "The conversion logics are 24 hours in a day, 7 days in a week, 4.35 weeks in a month, 30 days in a month"
            "For example, '7 days' should be returned as 168. "
            "For example, '3 months' should be returned as 2192. "
            "Return only the numeric value, without units. "
            "Must be a single integer value."
            "Do not include units like 'hours' or 'hr'."
        )
    )
    filepath: str
    confidence_score: float = Field(
        ge=0.0, 
        le=1.0,
        description="Confidence score between 0 and 1"
    )
    explanation: str