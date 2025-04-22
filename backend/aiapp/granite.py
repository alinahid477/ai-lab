from pydantic import BaseModel, Field
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from outlines import models, generate
from pydantic import BaseModel, Field
import utils
import re

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
    confidence_score: float = Field(
        ge=0.0, 
        le=1.0,
        description="Confidence score between 0 and 1"
    )


cmd_model_path = "ibm-granite/granite-3.1-1b-a400m-base"
chat_model_path = "ibm-granite/granite-3.0-2b-instruct"
device = "cuda" if torch.cuda.is_available() else "cpu"
chat_llm = AutoModelForCausalLM.from_pretrained(chat_model_path, device_map="cpu")
chat_tokenizer = AutoTokenizer.from_pretrained(chat_model_path, input_tokens=2048)
chat_model = models.Transformers(chat_llm, chat_tokenizer)

cmd_llm = AutoModelForCausalLM.from_pretrained(cmd_model_path, device_map="cpu")
cmd_tokenizer = AutoTokenizer.from_pretrained(cmd_model_path, input_tokens=2048)
cmd_model = models.Transformers(cmd_llm, cmd_tokenizer)



async def send_message_to_ws(message):
    utils.send_to_websocket_sync({"type": "terminalinfo", "data": message})

async def get_intended_command(english_command):
    prepared_commands = ["logs", "csvlogs", "kafkalogs", "classifylogs", "summarizelogs"]

    await send_message_to_ws(f"Asking Granite to find command: \"{english_command}\"")

    prompt_template_path = "/aiapp/prompt_files/get_intended_command_prompt_template.txt"
    with open(prompt_template_path, "r") as file:
        prompt_template = file.read()
    prompt = prompt_template.format(
                query=english_command,
                model_schema=SentenceAnalysis.model_json_schema(),
            )
    generator = generate.json(cmd_model, SentenceAnalysis)
    output = generator(prompt)
    print(f"output: {output}")
    if output.command not in prepared_commands:
        await send_message_to_ws(f"Invalid command: {output.command}. Must be one of {prepared_commands}")
        await send_message_to_ws(f"Asking Granite to simply answer: \"{english_command}\"")
        chat = [
            { "role": "user", "content": english_command },
        ]
        chat = chat_tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
        input_tokens = chat_tokenizer(chat, return_tensors="pt").to(device)
        output = chat_llm.generate(**input_tokens, 
                        max_new_tokens=100)
        output = chat_tokenizer.batch_decode(output)
        if len(output) > 0:
            pattern = re.compile(r'<\|start_of_role\|>(.*?)<\|end_of_role\|>(.*?)(?=<\|start_of_role\|>|$)')
            print(f"output-simple-english: {output[0]}")
            matches = pattern.findall(output[0])
            print(f"matches: {matches}")
            result = {}
            for match in matches:
                key = match[0]
                value = match[1].replace('<|end_of_text|>', '').strip()  # Strip <|end_of_text|> from the value
                result[key] = value
            print(result)
            if "assistant" in result:
                output = result['assistant']
            else:
                await send_message_to_ws(f"ERROR: Invalid response from AI. No 'assistant' key found.")
        else:
            await send_message_to_ws(f"ERROR: Invalid response from AI. The output is not an array or does not have any content to process.")
        

        # generator = generate.text(model)
        # result = generator("Question: {english_command} Answer:", max_tokens=100)
        
        # await send_message_to_ws(f"response from Granite: {output}")
    return output
    # utils.send_to_websocket({"type": "get_intended_command", "data": {output}})