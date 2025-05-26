
import os
import aiohttp
from helpers import utils
import time
import json

COMMAND_AI_MODEL_NAME = os.getenv("COMMAND_AI_MODEL_NAME")
COMMAND_AI_ENDPOINT = os.getenv("COMMAND_AI_ENDPOINT")
CHAT_AI_MODEL_NAME = os.getenv("CHAT_AI_MODEL_NAME")
CHAT_AI_ENDPOINT = os.getenv("CHAT_AI_ENDPOINT")
CHAT_AI_AUTH_TOKEN=os.getenv("CHAT_AI_AUTH_TOKEN")
AI_API_MAX_RETRY=3

conversation_history = [
    {"role": "system", "content": "You are a helpful assistant."}
]


async def callAIForSummarization(prompt, format = "json", modelname=None ,keep_alive = "0"):

  model_name=CHAT_AI_MODEL_NAME
  if modelname is not None:
      model_name = modelname
  
  if model_name == CHAT_AI_MODEL_NAME:
    url = CHAT_AI_ENDPOINT
  elif model_name == COMMAND_AI_MODEL_NAME:
    url = COMMAND_AI_ENDPOINT

  headers = {
    "Content-Type": "application/json"
  }
  
  headers["Authorization"] = f"Bearer {CHAT_AI_AUTH_TOKEN}"

  conversation_history = [{"role": "system", "content": "You are a helpful assistant."}]
  conversation_history.append({"role": "user", "content": prompt})

  estimated_tokens = utils.estimate_tokens(prompt)

  payload = {
        "model": model_name,
        "messages": conversation_history[-5:],  # Keep only the last 5 messages
        "format": format,
        "options": {
          "num_ctx": estimated_tokens + 30,
          "temperature": 0.7,
          "top_p": 1
        },
        "stream": False,
        "keep_alive": keep_alive 
      }
    

  count=0
  while count < AI_API_MAX_RETRY:
    count +=1
    try:
      print(f"calling --> {url}, {model_name}, tokens: {estimated_tokens}")
      async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
          if response.status == 200:
            data = await response.json()
            # Extract the assistant's reply
            # print(data)
            assistant_message = data["message"]["content"].strip()
            data["response"] = assistant_message
            return data
          else:
            text = await response.text()
            raise Exception(f"Error {response.status}: {text}")
    except Exception as e:
      print(f"ERROR making AI API call: {e}")
      time.sleep(60)




async def callAIForCommand(prompt, format = "json", modelname=None ,keep_alive = "0"):

  headers = {
    "Content-Type": "application/json"
  }   
  
  headers["Authorization"] = f"Bearer {CHAT_AI_AUTH_TOKEN}"
  

  model_name=COMMAND_AI_MODEL_NAME
  if modelname is not None:
    if modelname == "chat":
      model_name = CHAT_AI_MODEL_NAME
    else:
      model_name = modelname
  
  if model_name == CHAT_AI_MODEL_NAME:
    url = CHAT_AI_ENDPOINT
  elif model_name == COMMAND_AI_MODEL_NAME:
    url = COMMAND_AI_ENDPOINT

  estimated_tokens=0

  if model_name == CHAT_AI_MODEL_NAME:
    conversation_history.append({"role": "user", "content": prompt})
    if len(conversation_history) > 10:
      # Remove the oldest messages to keep only the last 10
      conversation_history[:] = conversation_history[-10:]
    estimated_tokens = utils.estimate_tokens(conversation_history)
    payload = {
          "model": model_name,
          "messages": conversation_history[-5:],  # Keep only the last 5 messages
          # "format": format,
          "options": {
            "num_ctx": estimated_tokens + 500,
            "temperature": 0.7,
            "top_p": 1
          },
          "stream": False,
          "keep_alive": keep_alive 
      }
  elif model_name == COMMAND_AI_MODEL_NAME:
    payload = {
          "model": model_name,
          "prompt": prompt,
          "stream": False,
          "keep_alive": keep_alive,
          "format": format
      }
  
  
  count=0
  while count < AI_API_MAX_RETRY:
    count +=1
    try:
      print(f"calling ({count}) --> {url}, {model_name}, tokens: {estimated_tokens}")
      async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
          if response.status == 200:
            data = await response.json()
            assistant_message = None
            if "message" in data:
              assistant_message = data["message"]["content"].strip()
            elif "response" in data:
              # Extract the assistant's reply
              assistant_message=data["response"].strip()
            if assistant_message:
              data["response"] = assistant_message
              # Append the assistant's reply to the conversation history
              conversation_history.append({"role": "assistant", "content": assistant_message})
              return data
            else:
              raise Exception(f"No reponse or message in data: {data}")  
          else:
            text = await response.text()
            raise Exception(f"Error {response.status}: {text}")
    except Exception as e:
      print(f"ERROR making AI API call: {e}")
      time.sleep(60)     


async def callAINOTUSED(purpose, prompt, format = "json", modelname=None ,keep_alive = "5m"):

  # print(f"callAI: {purpose}, {prompt}, {format}, {keep_alive}")
  if modelname == None:
    modelname=COMMAND_AI_MODEL_NAME
  else:
    model_name = modelname
  url = COMMAND_AI_ENDPOINT
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
    model_name = CHAT_AI_MODEL_NAME
    url = CHAT_AI_ENDPOINT
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
    headers["Authorization"] = f"Bearer {CHAT_AI_AUTH_TOKEN}"

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

