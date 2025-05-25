
import os
import aiohttp
import utils
import time


command_ai_model_name = os.getenv("COMMAND_AI_MODEL_NAME")
chat_ai_model_name = os.getenv("CHAT_AI_MODEL_NAME")
conversation_history = [
    {"role": "system", "content": "You are a helpful assistant."}
]

AI_API_MAX_RETRY=3

async def callAIForSummarization(prompt, format = "json", modelname=None ,keep_alive = "0"):

  model_name=chat_ai_model_name
  if modelname is not None:
      model_name = modelname
  
  if model_name == chat_ai_model_name:
    url = os.getenv("CHAT_AI_ENDPOINT")
  elif model_name == command_ai_model_name:
    url = os.getenv("COMMAND_AI_ENDPOINT")

  headers = {
    "Content-Type": "application/json"
  }
  authtoken=os.getenv("CHAT_AI_AUTH_TOKEN")
  headers["Authorization"] = f"Bearer {authtoken}"

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




async def callAIForCommand(prompt, format = "json", modelname=None ,keep_alive = "1m"):

  headers = {
    "Content-Type": "application/json"
  }   
  authtoken=os.getenv("CHAT_AI_AUTH_TOKEN")
  headers["Authorization"] = f"Bearer {authtoken}"
  

  model_name=command_ai_model_name
  if modelname is not None:
      model_name = modelname
  
  if model_name == chat_ai_model_name:
    url = os.getenv("CHAT_AI_ENDPOINT")
  elif model_name == command_ai_model_name:
    url = os.getenv("COMMAND_AI_ENDPOINT")

  estimated_tokens = utils.estimate_tokens(prompt)

  if model_name == chat_ai_model_name:
    conversation_history.append({"role": "user", "content": prompt})
    if len(conversation_history) > 10:
      # Remove the oldest messages to keep only the last 10
      conversation_history[:] = conversation_history[-10:]
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
  elif model_name == command_ai_model_name:
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
      print(f"calling --> {url}, {model_name}")
      async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
          if response.status == 200:
            data = await response.json()
            # Extract the assistant's reply
            assistant_message = data["choices"][0]["message"]["content"].strip()
            data["response"] = assistant_message
            # Append the assistant's reply to the conversation history
            conversation_history.append({"role": "assistant", "content": assistant_message})
            return data
          else:
            text = await response.text()
            raise Exception(f"Error {response.status}: {text}")
    except Exception as e:
      print(f"ERROR making AI API call: {e}")
      time.sleep(60)     
