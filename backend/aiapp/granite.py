from pydantic import BaseModel, Field
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from outlines import models, generate
from pydantic import BaseModel, Field
import utils
import re
import pandas as pd
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
    time_duration: int = Field(
        description=(
            "Time duration in hours. "
            "Convert any duration expressed in other units (e.g., days) to hours. "
            "For example, '7 days' should be returned as 168. "
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


cmd_model_path = "ibm-granite/granite-3.1-1b-a400m-base"
chat_model_path = "ibm-granite/granite-3.0-2b-instruct"
device = "cuda" if torch.cuda.is_available() else "cpu"
chat_llm = AutoModelForCausalLM.from_pretrained(chat_model_path, device_map="cpu")
chat_tokenizer = AutoTokenizer.from_pretrained(chat_model_path, input_tokens=2048)
chat_model = models.Transformers(chat_llm, chat_tokenizer)

cmd_llm = AutoModelForCausalLM.from_pretrained(cmd_model_path, device_map="cpu")
# cmd_tokenizer = AutoTokenizer.from_pretrained(cmd_model_path, input_tokens=2048)
cmd_tokenizer = AutoTokenizer.from_pretrained(cmd_model_path, trust_remote_code=True)
# cmd_model = models.Transformers(cmd_llm, cmd_tokenizer)
cmd_model = AutoModelForCausalLM.from_pretrained(cmd_model_path, device_map=device, trust_remote_code=True)


async def send_message_to_ws(message):
  utils.send_to_websocket_sync({"type": "terminalinfo", "data": message})



async def summarize_logs(logs_csv_file_path):
  print(f"HERE 0 {logs_csv_file_path}")
  prompt_template_path = "/aiapp/prompt_files/summarize_prompt_template.txt"

  with open(prompt_template_path, "r") as file:
    prompt_template = file.read()

  print(f"HERE 1 {logs_csv_file_path}")
  df = pd.read_csv(logs_csv_file_path)
  print(f"HERE 2")
  # Create a list to store the text lines
  text_lines = []

  # Iterate over each row in the DataFrame
  for index, row in df.iterrows():
      action = "threw" if row['classification'] != "info" else "output"
      text_line = f"LOGID-{index} {row['timestamp']} application: {row['app_name']} in namespace: {row['namespace_name']} {action} {row['classification']}: {row['message']}"
      text_lines.append(text_line)
  print(f"HERE 3")
  # # Print the first 5 lines of text_lines
  # for line in text_lines[:5]:
  #     print(line)

  chat = prompt_template.format(
                  log_type="application",
                  logs=text_lines,
                  model_schema=LogAnalysis.model_json_schema(),
                  stress_prompt="""You are a computer security intern that's really stressed out. 
                  
                  Use "um" and "ah" a lot.""",
              )
  print(f"HERE 4.1")
  input_tokens = cmd_tokenizer(chat, return_tensors="pt").to(device)
  print(f"HERE 4.2 {input_tokens}")
  try:
    # generate output tokens
    output = cmd_model.generate(**input_tokens, 
                          max_new_tokens=100)
  except Exception as e:
    print(e)
  print(f"HERE 4.3")
  # decode output tokens into text
  output = cmd_tokenizer.batch_decode(output)
  # print output
  print(f"summary: {output}")

  return output




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
            pattern = re.compile(r'<\|start_of_role\|>(.*?)<\|end_of_role\|>(.*?)(?=<\|start_of_role\|>|$)', re.DOTALL)
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