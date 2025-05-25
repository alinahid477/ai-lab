import json
import utils
import asyncio

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


if __name__ == "__main__":
  # test_prompt = "why do i need a K8s"
  # response = asyncio.run(get_intended_command("{}"))
  # print(response)

  # print("\n\n=========================================\n\n")
  # test_prompt = "can I consider openshift for this"
  # response = asyncio.run(get_intended_command("{\"command\":\"none\"}"))
  # print(response)

  asyncio.run(testMerge())


