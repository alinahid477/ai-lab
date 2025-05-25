import json
import utils
import asyncio
import re
from helpers.merge_log_summarization import smalltest 

async def send_message_to_ws(message):
  print(f"**sending to ws: {message}")
  try:
    utils.send_to_websocket_sync({"type": "terminalinfo", "data": message})
  except Exception as e:
    print("SMWS EXCEPTION")


async def get_intended_command(response_text):
    try:
        print (response_text)
        parsed_json = json.loads(response_text)
        prepared_commands = ["logs", "csvlogs", "kafkalogs", "classifylogs", "summarizelogs"]
        await send_message_to_ws(f"Text extracted for command: {parsed_json}")
        if parsed_json.get("command") not in prepared_commands:
            await send_message_to_ws(f"HERE ANother")
            return "NO CMD"
        
        return "CMD"
    except Exception as e:
       print(f"EXCEPTION {e}")



async def testMerge():
  await smalltest()



async def testOutput():
  obj =  {
            "output": "1. Frequent use of deprecated APIs ('getCustomerDetails') and 'ExportToCSV') necessitates immediate migration to compatible alternatives to prevent future issues.\n\n2. Recurring security alerts related to unusual login attempts (multiple IP addresses) indicate potential unauthorized access and require investigation.\n. High frequency of RAID array failures, potentially linked to system load or specific hardware components, poses a critical stability risk and demands immediate investigation.\n4. Lead conversion failures, often linked to missing contact information, highlight data integrity or synchronization issues within lead generation processes.\n5. Legacy authentication methods are flagged for deprecation, presenting a significant security risk and requiring prioritized migration to modern authentication systems."
        }
  observations_output=obj["output"]
  matches = re.findall(r'(?:\d+\.\s*)?(.*?)(?=\n\n\d+\.|\n\d+\.|\n\n|\n|\Z)', observations_output.strip(), re.DOTALL)
  matches = [obs.strip() for obs in matches if obs.strip()]
  observations = []
  count=0
  pattern = re.compile(r'^\s*((?:\d+)?\.)\s*(.*)$')
  for value in matches:
      m = pattern.match(value)
      if m:
        prefix, sentence = m.groups()
      else:
        # no bullet found → treat entire line as sentence
        prefix, sentence = None, value.strip()
      if sentence:
        count +=1
        observations.append(f"{count}: {sentence}")
  print(f"summarised observations: {len(observations)}")
  for i in observations:
     print(i)

if __name__ == "__main__":
  # test_prompt = "why do i need a K8s"
  # response = asyncio.run(get_intended_command("{}"))
  # print(response)

  # print("\n\n=========================================\n\n")
  # test_prompt = "can I consider openshift for this"
  # response = asyncio.run(get_intended_command("{\"command\":\"none\"}"))
  # print(response)

  asyncio.run(testMerge())


