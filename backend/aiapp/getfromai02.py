import utils
from classes.SentenceAnalysis import SentenceAnalysis
import aiohttp
import asyncio
import re
import json
import os

conversation_history = [
    {"role": "system", "content": "You are a helpful assistant."}
]
async def callAI(purpose, prompt, format = "json", keep_alive = "5m"):

  # print(f"callAI: {purpose}, {prompt}, {format}, {keep_alive}")
  model_name = "ilab-trained-granite-7b"
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
    ai_response = await callAI("command", prompt, "json", "0m")
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


if __name__ == "__main__":
  test_prompt = "why do i need a K8s"
  response = asyncio.run(get_intended_command(test_prompt))
  print(response)

  print("\n\n=========================================\n\n")
  test_prompt = "can I consider openshift for this"
  response = asyncio.run(get_intended_command(test_prompt))
  print(response)