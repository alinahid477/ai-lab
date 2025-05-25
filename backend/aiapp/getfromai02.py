import utils
from classes.SentenceAnalysis import SentenceAnalysis
from classes.LogAnalysis import LogAnalysis
from backend.aiapp.helpers import merge_log_summarization

import asyncio
import json
import os
import pandas as pd
from sentence_transformers import SentenceTransformer






async def callAI2(purpose, prompt, format = "json", modelname="noparampassed" ,keep_alive = "5m"):

  # print(f"callAI: {purpose}, {prompt}, {format}, {keep_alive}")
  if modelname == "noparampassed":
    modelname=command_ai_model_name

  model_name = modelname
  url = os.getenv("COMMAND_AI_ENDPOINT")
  payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "keep_alive": keep_alive
    }
  if format == "json":
    payload["format"] = "json"
  headers = {
    "Content-Type": "application/json"
  }
  # if purpose == "summarize":
  #   model_name = chat_ai_model_name
  #   url = os.getenv("COMMAND_AI_ENDPOINT")
  #   payload["options"] = {
  #     "num_ctx": 30000
  #   }

  if purpose != "command":
    model_name = chat_ai_model_name
    url = os.getenv("CHAT_AI_ENDPOINT")
    if purpose == "summarize":
      conversation_history.clear()  
    conversation_history.append({"role": "user", "content": prompt})
    if len(conversation_history) > 10:
      # Remove the oldest messages to keep only the last 10
      conversation_history[:] = conversation_history[-10:]
    payload = {
        "model": model_name,
        "messages": conversation_history[-5:],  # Keep only the last 5 messages
        "temperature": 0.7,
        "top_p": 1 
    }
    authtoken=os.getenv("CHAT_AI_AUTH_TOKEN")
    headers["Authorization"] = f"Bearer {authtoken}"

  print(f"calling --> {url}, {model_name}")
  async with aiohttp.ClientSession() as session:
    async with session.post(url, json=payload, headers=headers) as response:
      if response.status == 200:
        data = await response.json()
        if purpose != "command":
          # Extract the assistant's reply
          assistant_message = data["choices"][0]["message"]["content"].strip()
          data["response"] = assistant_message
          # Append the assistant's reply to the conversation history
          if purpose != "summarize":
            conversation_history.append({"role": "assistant", "content": assistant_message})
        return data
      else:
        text = await response.text()
        raise Exception(f"Error {response.status}: {text}")

async def send_message_to_ws(message):
  print(f"**sending to ws: {message}")
  try:
    utils.send_to_websocket_sync({"type": "terminalinfo", "data": message})
  except Exception as e:
    print("")

async def get_intended_command(english_command):
  output = None
  prepared_commands = ["logs", "csvlogs", "kafkalogs", "classifylogs", "summarizelogs"]

  await send_message_to_ws(f"Asking Granite to find command: \"{english_command}\"")

  prompt_template_path = "/aiapp/prompt_files/get_intended_command_prompt_template.txt"
  with open(prompt_template_path, "r") as file:
    prompt_template = file.read()
  prompt = prompt_template.format(
              query=english_command,
              model_schema=SentenceAnalysis.model_json_schema(),
          )
    
  try:
    ai_response = await callAI("command", prompt, "json", command_ai_model_name , "0m")
    if "response" in ai_response:
      response_text = ai_response["response"]
      parsed_json = json.loads(response_text)
      await send_message_to_ws(f"Text extracted for command: {parsed_json}")
      if parsed_json.get("command") not in prepared_commands:
        if parsed_json.get("command"):
          await send_message_to_ws(f"Invalid command: {parsed_json['command']}. Must be one of {prepared_commands}")
        else:
          await send_message_to_ws(f"Invalid command: {parsed_json}. Must be one of {prepared_commands}")
        await send_message_to_ws(f"Asking Granite to simply answer: \"{english_command}\"")
        ai_response = await callAI("english", english_command, "text")
        if "response" in ai_response:
          output = ai_response["response"]
      else:
        output = parsed_json

  except Exception as e:
    print(f"Error while calling AI endpoint: {e}")
    return None


  return output


def estimate_tokens(line):
    return len(line) // 4 + (1 if len(line) % 4 != 0 else 0)

# summarize logs from file /tmp/test3.notgit.csv
async def summarize_logs(logs_csv_file_path):
  
  # Initialize the embedding model
  embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


  prompt_template_path = "/aiapp/prompt_files/summarize_prompt_template2.txt"
  with open(prompt_template_path, "r") as file:
    prompt_template = file.read()

  df = pd.read_csv(logs_csv_file_path)
  
  # ai_response_history = []
  master_summary_obj={}
  MAX_TOKENS=15000
  consumed_tokens=0
  # Create a list to store the text lines
  text_lines = []
  # Iterate over each row in the DataFrame
  for index, row in df.iterrows():
    action = "threw" if row['classification'] != "info" else "output"
    text_line = f"LOGID-{index} {row['timestamp']} application: {row['app_name']} in namespace: {row['namespace_name']} {action} {row['classification']}: {row['message']}"
    if consumed_tokens < MAX_TOKENS:
      text_lines.append(text_line)
      consumed_tokens += estimate_tokens(text_line)
    else:
      print(f"CONTEXT: {index}--->{consumed_tokens}")
      consumed_tokens=0
      text_lines_str="\n".join(f"\"{line}\"," for line in text_lines)
      prompt = prompt_template.format(
                      log_type="application",
                      logs=text_lines_str,
                      # model_schema=LogAnalysis.model_json_schema(),
                      stress_prompt="""You are a computer security intern that's really stressed out. 
                      Use "um" and "ah" a lot.""",
                  )
      text_lines.clear()
      ai_response = await callAI3("summarize", prompt, LogAnalysis.model_json_schema())
      response_text = ai_response["response"]
      if len(master_summary_obj) < 1:
        master_summary_obj = json.load(response_text)
      else:
        merge_log_summarization.merge(master_summary_obj, json.load(response_text), embedding_model)
      # ai_response_history.append(response_text)
      print("\n\n")
  if len(text_lines) > 0:
    consumed_tokens=0
    text_lines_str="\n".join(f"\"{line}\"," for line in text_lines)
    prompt = prompt_template.format(
                    log_type="application",
                    logs=text_lines_str,
                    model_schema=LogAnalysis.model_json_schema(),
                    stress_prompt="""You are a computer security intern that's really stressed out. 
                    Use "um" and "ah" a lot.""",
                )
    text_lines.clear()
    ai_response = await callAI3("summarize", prompt, LogAnalysis.model_json_schema())
    response_text = ai_response["response"]
    merge_log_summarization.merge(master_summary_obj, json.load(response_text), embedding_model)
    # ai_response_history.append(response_text)
    print(f"CONTEXT: {index} --> {response_text}")

  print("==================================================================")
  print("==================================================================")
  print("==================================================================")
  print("==================================================================")
  print (ai_response_history)

  return

  # print(f"HERE 3")
  # # Print the first 5 lines of text_lines
  # for line in text_lines[:5]:
  #     print(line)
  text_lines_str="\n".join(f"\"{line}\"," for line in text_lines)
  prompt = prompt_template.format(
                  log_type="application",
                  logs=text_lines_str,
                  model_schema=LogAnalysis.model_json_schema(),
                  stress_prompt="""You are a computer security intern that's really stressed out. 
                  
                  Use "um" and "ah" a lot.""",
              )
  # print(f"HERE 4.1")
  # input_tokens = cmd_tokenizer(prompt, return_tensors="pt").to(device)
  output = {}
  try:
    # generate output tokens
    # output = cmd_model.generate(**input_tokens, 
    #                       max_new_tokens=100)
    # generator = generate.json(cmd_model, LogAnalysis)
    # print(generator)
    # output = list(generator(prompt))
    ai_response = await callAI("summarize", prompt, "text")
    if "response" in ai_response:
      response_text = ai_response["response"]
      output = json.loads(response_text)
  except Exception as e:
    print(e)
  
  # decode output tokens into text
  # output = cmd_tokenizer.batch_decode(output)
  # print output
  # print(f"summary: {output}")

  return output



if __name__ == "__main__":
  # test_prompt = "why do i need a K8s"
  # response = asyncio.run(get_intended_command(test_prompt))
  # print(response)

  # print("\n\n=========================================\n\n")
  # test_prompt = "can I consider openshift for this"
  # response = asyncio.run(get_intended_command(test_prompt))
  # print(response)

  asyncio.run(summarize_logs("/tmp/logs/classified_20156.nogit.csv"))
  