import utils
from classes.SentenceAnalysis import SentenceAnalysis
import aiohttp
import asyncio
import re
import json

async def callAI(prompt, format = "json", keep_alive = "5m"):
  url = "http://host.docker.internal:11434/api/generate"
  payload = {
        "model": "granite-3.3-2b-instruct",
        "prompt": prompt,
        "stream": False,
        "keep_alive": keep_alive
    }
  if format == "json":
    payload["format"] = "json"

  async with aiohttp.ClientSession() as session:
    async with session.post(url, json=payload) as response:
      if response.status == 200:
        data = await response.json()
        return data
      else:
        text = await response.text()
        raise Exception(f"Error {response.status}: {text}")
          

async def send_message_to_ws(message):
  print(f"**sending to ws: {message}")
  utils.send_to_websocket_sync({"type": "terminalinfo", "data": message})

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
    ai_response = await callAI(prompt, "json", "0m")
    # Assume `response_data` is your REST response dictionary
    if "response" in ai_response:
      response_text = ai_response["response"]
      parsed_json = json.loads(response_text)
      await send_message_to_ws(f"Text extracted for command: {parsed_json}")
      if parsed_json['command'] not in prepared_commands:
        await send_message_to_ws(f"Invalid command: {parsed_json['command']}. Must be one of {prepared_commands}")
        await send_message_to_ws(f"Asking Granite to simply answer: \"{english_command}\"")
        ai_response = await callAI(english_command, "text")
        if "response" in ai_response:
          output = ai_response["response"]
    else:
      output = parsed_json

    
  except Exception as e:
    print(f"Error while calling AI endpoint: {e}")
    return None

  # print(f"output: {output}")
  # if output.command not in prepared_commands:
  #     await send_message_to_ws(f"Invalid command: {output.command}. Must be one of {prepared_commands}")
  #     await send_message_to_ws(f"Asking Granite to simply answer: \"{english_command}\"")
  #     chat = [
  #         { "role": "user", "content": english_command },
  #     ]
  #     chat = chat_tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
  #     input_tokens = chat_tokenizer(chat, return_tensors="pt").to(device)
  #     output = chat_llm.generate(**input_tokens, 
  #                     max_new_tokens=100)
  #     output = chat_tokenizer.batch_decode(output)
  #     if len(output) > 0:
  #         pattern = re.compile(r'<\|start_of_role\|>(.*?)<\|end_of_role\|>(.*?)(?=<\|start_of_role\|>|$)', re.DOTALL)
  #         print(f"output-simple-english: {output[0]}")
  #         matches = pattern.findall(output[0])
  #         print(f"matches: {matches}")
  #         result = {}
  #         for match in matches:
  #             key = match[0]
  #             value = match[1].replace('<|end_of_text|>', '').strip()  # Strip <|end_of_text|> from the value
  #             result[key] = value
  #         print(result)
  #         if "assistant" in result:
  #             output = result['assistant']
  #         else:
  #             await send_message_to_ws(f"ERROR: Invalid response from AI. No 'assistant' key found.")
  #     else:
  #         await send_message_to_ws(f"ERROR: Invalid response from AI. The output is not an array or does not have any content to process.")
      

      # generator = generate.text(model)
      # result = generator("Question: {english_command} Answer:", max_tokens=100)
      
      # await send_message_to_ws(f"response from Granite: {output}")
  return output
  # utils.send_to_websocket({"type": "get_intended_command", "data": {output}})


if __name__ == "__main__":
  test_prompt = "tell me about openshift"
  response = asyncio.run(get_intended_command(test_prompt))
  print(response)