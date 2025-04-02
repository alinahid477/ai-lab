from pydantic import BaseModel, Field
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from outlines import models, generate
from pydantic import BaseModel, Field
import utils


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


class CommandParameter(BaseModel):
    name: str
    value: str

class SentenceAnalysis(BaseModel):
    command: str
    followup: str
    time_duration: str
    file: str
    confidence_score: float


model_path = "ibm-granite/granite-3.1-1b-a400m-base"
device = "cuda" if torch.cuda.is_available() else "cpu"
llm = AutoModelForCausalLM.from_pretrained(model_path, device_map="cpu")
tokenizer = AutoTokenizer.from_pretrained(model_path, input_tokens=2048)
model = models.Transformers(llm, tokenizer)



async def send_message_to_ws(message):
    await utils.send_to_websocket({"type": "terminalinfo", "data": message})

async def get_intended_command(english_command):
    
    prepared_commands = ["csvlogs", "kafkalogs", "classifylogs", "Summarizelogs"]

    print("debug 0")
    await send_message_to_ws(f"Asking Granite to find command: \"{english_command}\"")

    prompt_template_path = "/aiapp/prompt_files/get_intended_command_prompt_template.txt"
    with open(prompt_template_path, "r") as file:
        prompt_template = file.read()
    prompt = prompt_template.format(
                query=english_command,
                model_schema=SentenceAnalysis.model_json_schema(),
            )
    generator = generate.json(model, SentenceAnalysis)
    output = generator(prompt)
    print("debug 1 {output}")
    if output.command not in prepared_commands:
        print("debug 1")
        await send_message_to_ws(f"Invalid command: {output.command}. Must be one of {prepared_commands}")
        await send_message_to_ws(f"Asking Granite to simply answer: \"{english_command}\"")
        output = generate.text(model)
        print("debug 2")
        await send_message_to_ws("response from Granite: \"{output}\"")
    return output
    # utils.send_to_websocket({"type": "get_intended_command", "data": {output}})