from pydantic import BaseModel, Field


class SecurityEvent(BaseModel):
    # The reasoning for why this event is relevant.
    reasoning: str

    # The type of event.
    event_type: str

    # Whether this event requires human review.
    requires_human_review: bool

    # The confidence score for this event. I'm not sure if this
    # is meaningful for language models, but it's here if we want it.
    confidence_score: float = Field(
        ge=0.0, 
        le=1.0,
        description="Confidence score between 0 and 1"
    )

    # Recommended actions for this event.
    recommended_actions: list[str]

class HardwareFailureEvent(BaseModel):
    # The reasoning for why this event is relevant.
    reasoning: str

    # The type of event.
    event_type: str

    # Whether this event requires human review.
    requires_human_review: bool

    # The confidence score for this event. I'm not sure if this
    # is meaningful for language models, but it's here if we want it.
    confidence_score: float = Field(
        ge=0.0, 
        le=1.0,
        description="Confidence score between 0 and 1"
    )

    # Recommended actions for this event.
    recommended_actions: list[str]



class LogAnalysis(BaseModel):
    # A summary of the analysis.
    summary: str

    # Observations about the logs.
    observations: list[str]

    # Planning for the analysis.
    planning: list[str]

    # Security events found in the logs.
    security_events: list[SecurityEvent]

    # harware failure events found in the logs.
    Hardware_failure_events: list[HardwareFailureEvent]

    # # Traffic patterns found in the logs.
    # traffic_patterns: list[WebTrafficPattern]

    # # The highest severity event found.
    # highest_severity: Optional[SeverityLevel]
    requires_immediate_attention: bool
