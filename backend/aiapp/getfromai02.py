from classes.SentenceAnalysis import SentenceAnalysis
from classes.LogAnalysis import LogAnalysis
from classes.GenericOutput import GenericOutput
from helpers import merge_log_summarization
from helpers import callAI
from helpers import utils

import asyncio
import json
import os
import pandas as pd
from sentence_transformers import SentenceTransformer

LOG_SUMMARY_MAX_TOKENS=15000



async def send_message_to_ws(message):
  print(f"**sending to ws: {message}")
  try:
    utils.send_to_websocket_sync({"type": "terminalinfo", "data": message})
  except Exception as e:
    print("")

async def get_intended_command(english_command):
  output = None
  prepared_commands = ["logs", "csvlogs", "kafkalogs", "classifylogs", "summarizelogs"]

  await send_message_to_ws(f"Asking trained model (Granite_7b) to find command: \"{english_command}\"")

  prompt_template_path = "/aiapp/prompt_files/get_intended_command_prompt_template.txt"
  with open(prompt_template_path, "r") as file:
    prompt_template = file.read()
  prompt = prompt_template.format(
              query=english_command,
          )
    
  try:
    ai_response = await callAI.callAIForCommand(prompt, SentenceAnalysis.model_json_schema())
    if "response" in ai_response:
      response_text = ai_response["response"]
      parsed_json = json.loads(response_text)
      await send_message_to_ws(f"command extracted: {parsed_json}")
      if parsed_json.get("command") not in prepared_commands:
        if parsed_json.get("command"):
          await send_message_to_ws(f"Invalid command: {parsed_json['command']}. Must be one of {prepared_commands}")
        else:
          await send_message_to_ws(f"Invalid command: {parsed_json}. Must be one of {prepared_commands}")
        await send_message_to_ws(f"Asking model (chat model) to simply answer: \"{english_command}\"")
        ai_response = await callAI.callAIForCommand(english_command, GenericOutput.model_json_schema(), "chat")
        if "response" in ai_response:
          output = ai_response["response"]
          await send_message_to_ws(f"response extracted: {output}")
      else:
        output = parsed_json

  except Exception as e:
    print(f"Error while calling AI endpoint: {e}")
    return None


  return output


# summarize logs from file /tmp/test3.notgit.csv
async def summarize_logs(logs_csv_file_path):
  

  print("LOGS SUMMARIZE START")

  # Initialize the embedding model
  embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


  prompt_template_path = "/aiapp/prompt_files/summarize_prompt_template2.txt"
  with open(prompt_template_path, "r") as file:
    prompt_template = file.read()

  df = pd.read_csv(logs_csv_file_path)
  
  tmp = prompt_template.format(
                    log_type="application",
                    logs="",
                    stress_prompt="""You are a helpful Site Reliability Engineer. You analyse application logs and provide summary""",
                )

  approx_prompt_token = utils.estimate_tokens(tmp)
  prev_index=0
  master_summary_obj={}
  consumed_tokens=approx_prompt_token
  text_lines = []
  # Iterate over each row in the DataFrame
  for index, row in df.iterrows():
    action = "threw" if row['classification'] != "info" else "output"
    text_line = f"LOGID-{index} {row['timestamp']} application: {row['app_name']} in namespace: {row['namespace_name']} {action} {row['classification']}: {row['message']}"
    if consumed_tokens < LOG_SUMMARY_MAX_TOKENS:
      text_lines.append(text_line)
      consumed_tokens += utils.estimate_tokens(text_line)
    else:
      print(f"CONTEXT: {prev_index}-{index}--->tokens: {consumed_tokens}")
      text_lines_str="\n".join(f"\"{line}\"," for line in text_lines)
      prompt = prompt_template.format(
                      log_type="application",
                      logs=text_lines_str,
                      stress_prompt="""You are a helpful Site Reliability Engineer. You analyse application logs and provide summary.""",
                    )
      consumed_tokens=approx_prompt_token
      prev_index=index
      text_lines.clear()
      ai_response = await callAI.callAIForSummarization(prompt, LogAnalysis.model_json_schema())
      response_text = ai_response["response"]
      if len(master_summary_obj) < 1:
        master_summary_obj = json.loads(response_text)
      else:
        print("merging summarization chunk with master...")
        await merge_log_summarization.merge(master_summary_obj, json.loads(response_text), embedding_model)
      # ai_response_history.append(response_text)
      print("\n\n")
  if len(text_lines) > 0:
    text_lines_str="\n".join(f"\"{line}\"," for line in text_lines)
    consumed_tokens = utils.estimate_tokens(text_lines_str) + approx_prompt_token
    prompt = prompt_template.format(
                    log_type="application",
                    logs=text_lines_str,
                    stress_prompt="""You are a helpful Site Reliability Engineer. You analyse application logs and provide summary.""",
                  )
    print(f"FINAL CONTEXT: {prev_index}-{index}--->tokens: {consumed_tokens}")
    ai_response = await callAI.callAIForSummarization(prompt, LogAnalysis.model_json_schema())
    response_text = ai_response["response"]
    print("merging FINAL summarization chunk with master...")
    await merge_log_summarization.merge(master_summary_obj, json.loads(response_text), embedding_model)

  print("\n\n...Final Compress...")
  merge_log_summarization.compress(master_summary_obj)
  print("...compress end....")
  print("\n\nLOGS SUMMARIZE END")

  return master_summary_obj



if __name__ == "__main__":
  # test_prompt = "why do i need a K8s"
  # response = asyncio.run(get_intended_command(test_prompt))
  # print(response)

  # print("\n\n=========================================\n\n")
  # test_prompt = "can I consider openshift for this"
  # response = asyncio.run(get_intended_command(test_prompt))
  # print(response)

  asyncio.run(summarize_logs("/tmp/logs/classified_20156.nogit.csv"))
  