import utils
from classes.SentenceAnalysis import SentenceAnalysis
from classes.LogAnalysis import LogAnalysis
import aiohttp
import asyncio
import json
import os
import pandas as pd

conversation_history = [
    {"role": "system", "content": "You are a helpful assistant."}
]
async def callAI(purpose, prompt, format = "json", modelname="ilab-trained-granite-7b" ,keep_alive = "5m"):

  # print(f"callAI: {purpose}, {prompt}, {format}, {keep_alive}")
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
  if purpose != "command":
    model_name = "granite-3-1-8b-instruct-w4a16"
    url = os.getenv("CHAT_AI_ENDPOINT")
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
    ai_response = await callAI("command", prompt, "json", "ilab-trained-granite-7b" , "0m")
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


# summarize logs from file /tmp/test3.notgit.csv
async def summarize_logs(logs_csv_file_path):
  # print(f"HERE 0 {logs_csv_file_path}")
  prompt_template_path = "/aiapp/prompt_files/summarize_prompt_template.txt"

  with open(prompt_template_path, "r") as file:
    prompt_template = file.read()

  # print(f"HERE 1 {logs_csv_file_path}")
  df = pd.read_csv(logs_csv_file_path)
  # print(f"HERE 2")
  # Create a list to store the text lines
  text_lines = []

  # Iterate over each row in the DataFrame
  for index, row in df.iterrows():
      action = "threw" if row['classification'] != "info" else "output"
      text_line = f"LOGID-{index} {row['timestamp']} application: {row['app_name']} in namespace: {row['namespace_name']} {action} {row['classification']}: {row['message']}"
      text_lines.append(text_line)
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

  asyncio.run(summarize_logs("/tmp/test3.nogit.csv"))
  