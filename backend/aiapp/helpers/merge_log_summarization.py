import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import aiohttp
import asyncio
import json
import re
from helpers.summary_analysis_reader import read_json_objects
from classes.GenericOutput import GenericOutput



conversation_history = [{"role": "system", "content": "You are a helpful IT systems logs analyst."}]


def estimate_tokens(line):
    return len(line) // 4 + (1 if len(line) % 4 != 0 else 0)


async def callAI(prompt, format = "json", keepHistory=False, clearHistory=True, modelname=None, keep_alive = "0"):
  # print(f"callAI: {purpose}, {prompt}, {format}, {keep_alive}")
  if modelname == None:
    model_name = os.getenv("CHAT_AI_MODEL_NAME")
    model_name = "gemma3:4b-it-qat"
  else:
    model_name = modelname

  url = os.getenv("CHAT_AI_ENDPOINT")
  url = "http://host.docker.internal:11434/api/chat"
  if clearHistory:
    conversation_history = [{"role": "system", "content": "You are a helpful IT systems logs analyst."}]

  conversation_history.append({"role": "user", "content": prompt})

  estimated_tokens = estimate_tokens(prompt)
  if keepHistory:
    # Remove the oldest messages to keep only the last 10
    if len(conversation_history) > 10:
      conversation_history[:] = conversation_history[-10:]

  payload = {
        "model": model_name,
        "messages": conversation_history[-5:],  # Keep only the last 5 messages
        "format": format,
        "options": {
          "num_ctx": estimated_tokens + 20,
          "temperature": 0.7,
          "top_p": 1
        },
        "stream": False,
        "keep_alive": keep_alive,
      }
  
  headers = {
    "Content-Type": "application/json"
  }
  authtoken=os.getenv("CHAT_AI_AUTH_TOKEN")
  headers["Authorization"] = f"Bearer {authtoken}"

  ai_call_count = 0
  while ai_call_count < 3:
    ai_call_count += 1
    try:
      print(f"calling --> {url}, {model_name}, {estimated_tokens}")
      async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
          if response.status == 200:
            data = await response.json()
            if "message" in data and "content" in data["message"]:
              assistant_message = data["message"]["content"].strip()
              data["response"] = assistant_message
              if keepHistory:
                conversation_history.append({"role": "assistant", "content": assistant_message})
            return data
          else:
            print("*****************************")
            txt = await response.text()
            raise Exception(f"Error {response.status}: {txt}")
    except Exception as e:
      print(f"EXCEPTION: {e}")
  return None

async def compress_summaries(master_summary, summariesArr):
  summaries_as_text=f"\nsummary 1:\n{master_summary}"
  idx=2
  for summary in summariesArr:
    summaries_as_text += f"\nsummary {idx}:\n{summary}"
    idx+=1

  prompt_template_path = "/aiapp/prompt_files/compress_summary_prompt.txt"
  with open(prompt_template_path, "r") as file:
    prompt_template = file.read()

  prompt = prompt_template.format(
                      numberofsummaries=len(summariesArr),
                      summaries=summaries_as_text,
                    )
  print(f"summarizing summaries: {idx}")
  data = await callAI(prompt, GenericOutput.model_json_schema())
  return data


async def compress_observations(observationsArr):
  
  observations_text = "\n".join(f"\"{line}\"," for line in observationsArr)
  
  prompt_template_path = "/aiapp/prompt_files/compress_observations_prompt.txt"
  with open(prompt_template_path, "r") as file:
    prompt_template = file.read()

  prompt = prompt_template.format(
                      numberofobservations=len(observationsArr),
                      observations=observations_text,
                    )
  print(f"summarising observations: {len(observationsArr)}")
  data = await callAI(prompt, GenericOutput.model_json_schema())
  return data

async def compress_planning(planningArr):
  
  planning_text = "\n".join(f"\"{line}\"," for line in planningArr)
  
  prompt_template_path = "/aiapp/prompt_files/compress_planning_prompt.txt"
  with open(prompt_template_path, "r") as file:
    prompt_template = file.read()

  prompt = prompt_template.format(
                      numberofplannings=len(planningArr),
                      plannings=planning_text,
                    )
  print(f"summarising plannings: {len(planningArr)}")
  data = await callAI(prompt, GenericOutput.model_json_schema())
  return data

async def compress_security_events(securityEventsArr):
  
  security_events_text = "\n".join(f"\"{line}\"," for line in securityEventsArr)
  
  prompt_template_path = "/aiapp/prompt_files/compress_security_events_prompt.txt"
  with open(prompt_template_path, "r") as file:
    prompt_template = file.read()

  prompt = prompt_template.format(
                      numberofsecurityevents=len(securityEventsArr),
                      security_events=security_events_text,
                    )
  print(f"summarising security_events: {len(securityEventsArr)}")
  data = await callAI(prompt, GenericOutput.model_json_schema())
  return data

async def compress_hardware_failure_events(hwFailureEventsArr):
  
  hw_failure_events_text = "\n".join(f"\"{line}\"," for line in hwFailureEventsArr)
  
  prompt_template_path = "/aiapp/prompt_files/compress_hw_failures_prompt.txt"
  with open(prompt_template_path, "r") as file:
    prompt_template = file.read()

  prompt = prompt_template.format(
                      numberofhwfailures=len(hwFailureEventsArr),
                      hwfailures=hw_failure_events_text,
                    )
  print(f"summarising hardware failure: {len(hwFailureEventsArr)}")
  data = await callAI(prompt, GenericOutput.model_json_schema())
  return data


async def compress (master_obj):
  
  # if len(master_obj["summaries"]) > 0:
  #   data = await compress_summaries(master_obj["summary"], master_obj["summaries"])
  #   if data and "response" in data:
  #     compressed_summary=None
  #     ai_msg_content = data["response"]
  #     try:
  #       obj = json.loads(ai_msg_content)
  #       compressed_summary=obj["output"]
  #     except Exception as e:
  #       if '"overall summary":' in ai_msg_content.lower():
  #         match = re.search(r'"Overall Summary":\s*"(.+?)",\s*"\w', ai_msg_content, re.DOTALL)
  #       elif '"merged_summary":' in ai_msg_content.lower():
  #         match = re.search(r'"merged_summary":\s*"(.+?)",\s*"\w', ai_msg_content, re.DOTALL)
  #       if match:
  #           compressed_summary = match.group(1)

  #     if compressed_summary:
  #       # Optional: Unescape any escaped characters like \'
  #       compressed_summary = compressed_summary.replace("\\'", "'")
  #       master_obj["summary"] = compressed_summary
  #       master_obj["summaries"] = []
  #     else:
  #         print(f"ERROR: Commpressed summary didn't work. AI RESPONSE: {ai_msg_content}")

  if len(master_obj["observations"]) > 5:
    data = await compress_observations(master_obj["observations"])
    matches=None
    if data and "response" in data:
      observations_text = data["response"]
      try:
        obj = json.loads(observations_text)
        observations_output=obj["output"]
        matches = re.findall(r'(?:\d+\.\s*)?(.*?)(?=\n\n\d+\.|\n\d+\.|\n\n|\n|\Z)', observations_output.strip(), re.DOTALL)
      except Exception as e:
        # Find all observation entries
        pattern = r'"(Observation \d+)":\s*"(.+?)"(?=,|\s*$)'
        matches = re.findall(pattern, observations_text, re.DOTALL)
      # Combine key and value into a single string per item
      observations = []
      if matches:
        for key, value in enumerate(matches, 1):
            clean_value = value.replace("\\'", "'")
            observations.append(f"{key}: {clean_value}")
        print(f"summarised observations: {len(observations)}")
        master_obj["observations"] = observations

  if len(master_obj["planning"]) > 5:
    matches=None
    data = await compress_planning(master_obj["planning"])
    if data and "response" in data:
      planning_text = data["response"]
      try:
        obj = json.loads(planning_text)
        pattern=obj["output"]
        pattern = re.findall(r'(.*?)(?:\n\s*\n|$)', pattern.strip(), re.DOTALL)
        matches = [obs.strip() for obs in pattern if obs.strip()]        
      except Exception as e:
        # Find all observation entries
        pattern = r'"(Planning \d+)":\s*"(.+?)"(?=,|\s*$)'
        matches = re.findall(pattern, planning_text, re.DOTALL)
      # Combine key and value into a single string per item
      # master_obj["planning"] = [f"{key}: {value.replace('\\\'', '\'')}" for key, value in matches]
      if matches:
        plannings = []
        for key, value in enumerate(matches, 1):
            clean_value = value.replace("\\'", "'")
            plannings.append(f"{key}: {clean_value}")
        print(f"summarised planning: {len(plannings)}")
        master_obj["planning"] = plannings
      
  if "security_events" in master_obj and len(master_obj["security_events"]) > 0:
    formatted_events = [
                        f"ID#{event['id']}: {event['reasoning']}"
                        for event in master_obj["security_events"]
                        ]
    data = await compress_security_events(formatted_events)
    if data and "response" in data:
      events_text = data["response"]
      try:
        obj = json.loads(events_text)
        events_text=obj["output"]
        # Extract all ID numbers
        id_numbers = re.findall(r'ID#(\d+)', events_text)
        if id_numbers and len(id_numbers) > 0:
          # Convert to integers (optional)
          id_numbers = [int(i) for i in id_numbers]
          # Filter events where id is in id_numbers
          matching_events = [event for event in master_obj["security_events"] if event["id"] in id_numbers]
          master_obj["security_events"] = matching_events
        else:
          raise Exception(f"ERROR: {events_text}")
      except Exception as e:
        print(f"Security events could not be compresses. {e}")

  if "hardware_failure_events" in master_obj and len(master_obj["hardware_failure_events"]) > 0:
    formatted_events = [
                        f"ID#{event['id']}: {event['reasoning']}"
                        for event in master_obj["hardware_failure_events"]
                        ]
    data = await compress_hardware_failure_events(formatted_events)
    if data and "response" in data:
      events_text = data["response"]
      try:
        obj = json.loads(events_text)
        events_text=obj["output"]
        # Extract all ID numbers
        id_numbers = re.findall(r'ID#(\d+)', events_text)
        if id_numbers and len(id_numbers) > 0:
          # Convert to integers (optional)
          id_numbers = [int(i) for i in id_numbers]
          # Filter events where id is in id_numbers
          matching_events = [event for event in master_obj["hardware_failure_events"] if event["id"] in id_numbers]
          master_obj["hardware_failure_events"] = matching_events
        else:
          raise Exception(f"ERROR: {events_text}")
      except Exception as e:
        print(f"HW failure events could not be compresses. {e}")

    
# Function to check if the new item is unique
async def is_similar(textItem, vector_db, embedding_model, threshold=0.85):

  # I found an anomily that there were these texts added in the observations section.
  # just hardcoding the handle of that.
  if textItem in {"planning", "security_events", "hardware_failure_events", "requires_immediate_attention"}:
    return True
  embedding = embedding_model.encode([textItem])
  normalized_embedding = embedding / np.linalg.norm(embedding)
  if vector_db.ntotal > 0:
      similarities, _ = vector_db.search(normalized_embedding, k=1)
      if similarities[0][0] >= threshold:
          # print("*****************")
          # print(f"Duplicate detected (similarity: {similarities[0][0]:.4f}). Skipping insertion.")
          # print("*****************")
          return True

  # cache it 
  # (this is so that for the nexitem test we utilise this cache; 
  # most likely the is_similar func is going to get called from a loop;
  # hence maintain a cache)
  vector_db.add(normalized_embedding)
  return False


async def dedupe_similar (masterArr, newArr, embedding_model):
  
  embedding_dim = embedding_model.get_sentence_embedding_dimension()

  # Initialize the FAISS index for inner product (cosine similarity)
  # this vector_db maintains what is in there already and the newitem is compared with it.
  # vector_db is used as cache
  vector_db = faiss.IndexFlatIP(embedding_dim)
  
  # load the vector_db with what is in the master.
  for item in masterArr:
    embedding = embedding_model.encode([item])
    normalized_embedding = embedding / np.linalg.norm(embedding)
    vector_db.add(normalized_embedding)  

  # test the new item. and if it is not similar to what is exisitng in the master already add it.
  # the way we test this similarity is by maintaining a vector_db cache.
  for item in newArr:
    isitsimilar= await is_similar(item, vector_db, embedding_model)
    if isitsimilar == False:
       # no similarity found. So add it in the master
       masterArr.append(item)
    else:
       print(f"similarity found: {item}")


async def merge (master_obj, new_obj, embedding_model):
  
  print("-----dedupe observations------")
  await dedupe_similar(master_obj["observations"], new_obj["observations"], embedding_model)
  # todo: if observation is more than 10 compress it into 5.
  print("-----dedupe planning------")
  await dedupe_similar(master_obj["planning"], new_obj["planning"], embedding_model)
  # todo: if planning is more than 10 compress it into 5.

  if "summaries" not in master_obj:
     master_obj["summaries"] = []

  master_obj["summaries"].append(new_obj["summary"])

  if "init" in master_obj and master_obj["init"]:
    new_security_events = [
      event for event in master_obj["security_events"]
      if event["confidence_score"] > 0.90 and "event_type" in event and "security" in event["event_type"].lower()
    ]
    master_obj["security_events"] = new_security_events
    new_hardware_events = [
      event for event in master_obj["hardware_failure_events"]
      if (event["confidence_score"] > 0.95 and event["confidence_score"] <= 1) or event["confidence_score"] > 95
    ]
    master_obj["hardware_failure_events"] = new_hardware_events
    # we only want to do this once. lets set a flag to mark it. 
    master_obj["init"] = True


  print("-----dedupe seurity------")
  # Lets process the merge of new_obj
  new_security_events = [
    event for event in new_obj["security_events"]
    if event["confidence_score"] > 0.90 and "event_type" in event and "security" in event["event_type"].lower()
  ]
  # Extract all reasoning texts into array
  new_reasonings = [event["reasoning"] for event in new_security_events]
  master_reasonings = [event["reasoning"] for event in master_obj["security_events"]]
  # dedupe the arrays. the below will place things inside master_reasoning
  await dedupe_similar(master_reasonings, new_reasonings, embedding_model)
  # now in order to get the rest of field for a security event (eg: eventype, confidence, reccommendation etc)
  #   we need to find the what are the new ones that were added to master in the dedupe process
  uncommon_set = set(master_reasonings).symmetric_difference(new_reasonings)
  uncommon = list(uncommon_set)
  # "uncommon" holds the new ones that are just been added.
  #   now, lets get the rest of the fileds.
  for event in new_obj["security_events"]:
     if event["reasoning"] in uncommon:
        master_obj["security_events"].append(event)
  # add an extra field called "id". This will come in handy for compress.
  for idx, event in enumerate(master_obj["security_events"], start=1):
    event["id"] = idx
  

  print("-----dedupe hw------")
  # same logic (as security_events) is used to dedupe harware_failures
  new_hardware_events = [
    event for event in new_obj["hardware_failure_events"]
    if (event["confidence_score"] > 0.95 and event["confidence_score"] <= 1) or event["confidence_score"] > 95
  ]
  # Extract all reasoning texts
  new_reasonings = [event["reasoning"] for event in new_hardware_events]
  master_reasonings = [event["reasoning"] for event in master_obj["hardware_failure_events"]]
  await dedupe_similar(master_reasonings, new_reasonings, embedding_model)
  uncommon_set = set(master_reasonings).symmetric_difference(new_reasonings)
  uncommon = list(uncommon_set)
  idx=1
  for event in new_obj["hardware_failure_events"]:
     if event["reasoning"] in uncommon:
        event["id"]=idx
        idx += 1
        master_obj["hardware_failure_events"].append(event)
  for idx, event in enumerate(master_obj["hardware_failure_events"], start=1):
    event["id"] = idx


  
async def smalltest():
  # Initialize the embedding model
  embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


  masterobj = {
    "summary": "This log analysis reveals several recurring issues including deprecated API endpoints, RAID array failures, and security alerts related to unusual login attempts. The system is experiencing frequent lead conversion failures, often due to missing contact information, and escalation rule failures, indicating potential issues with the workflow or data integrity. There's a clear pattern of security alerts and RAID array issues, suggesting a need for hardware maintenance and robust security monitoring.",
    "observations": [
      "The frequent use of the deprecated 'getCustomerDetails' API endpoint is a significant concern. The system should be migrated to the 'fetchCustomerInfo' endpoint as soon as possible to avoid future deprecation issues.",
      "RAID array failures are occurring regularly, indicating a potential hardware problem. Immediate investigation and repair are crucial to prevent data loss.",
      "Security alerts related to unusual login attempts are consistently observed. This suggests a need for stronger authentication mechanisms and more granular access control.",
      "Lead conversion failures are a recurring issue, likely stemming from incomplete or inaccurate lead data. This warrants a review of the lead data entry process and validation rules.",
      "Escalation rule failures are indicative of a flawed workflow or misconfigured rules. These need to be reviewed and corrected for proper system operation.",
      "There's a temporal pattern to the RAID failures, potentially linked to system load or a specific hardware component's lifespan."
    ],
    "planning": [
      "Prioritize hardware maintenance and RAID array diagnostics. Schedule a thorough inspection of the system's storage infrastructure.",
      "Immediately migrate the 'getCustomerDetails' API endpoint to 'fetchCustomerInfo'. Implement a phased migration plan to avoid disruption.",
      "Review and strengthen authentication mechanisms. Consider multi-factor authentication and role-based access control.",
      "Investigate the root cause of lead conversion failures. Implement data validation rules and improve lead data quality.",
      "Thoroughly review and correct the escalation rule definitions to ensure they align with the intended workflow.",
      "Implement enhanced monitoring and alerting for security events, focusing on unusual login activity and potential intrusions. "
    ],
    "security_events": [
      {
        "reasoning": "The consistent security alerts related to unusual login attempts, particularly outside of business hours, are highly concerning. This suggests a potential security breach or unauthorized access attempt. Requires immediate investigation and potential lockdown of affected accounts.",
        "event_type": "Security Breach",
        "requires_human_review": "true",
        "confidence_score": 0.85
      ,
        "recommended_actions": ["Investigate IP addresses", "Review user access logs", "Implement MFA", "Review network security"]
      },
      {
        "reasoning": "The frequent RAID array failures are a critical stability issue. Continued failures could lead to data loss and system downtime. Requires immediate hardware diagnostics and repair.",
        "event_type": "Hardware Failure",
        "requires_human_review": "true",
        "confidence_score": 0.9
      ,
        "recommended_actions": ["Run diagnostics", "Replace failing drives", "Review storage configuration"]
      },
      {
        "reasoning": "The repeated use of the deprecated API endpoint indicates a potential future issue. It is vital to migrate to the new endpoint to avoid disruption and maintain compatibility.",
        "event_type": "API Deprecation",
        "requires_human_review": "true",
        "confidence_score": 0.7
      ,
        "recommended_actions": ["Update code", "Test migrated code", "Monitor API performance"]
      }
    ],
    "hardware_failure_events": [
      {
        "reasoning": "The recurring RAID array failures indicate a serious hardware problem. This needs immediate attention to prevent data loss and system downtime.",
        "event_type": "RAID Array Failure",
        "requires_human_review": "true",
        "confidence_score": 0.95
      ,
        "recommended_actions": ["Run diagnostics", "Replace failing drives", "Review storage configuration"]
      },
      {
        "reasoning": "The potential for hardware issues is high given the frequent failures.  A hardware health check is required to determine the underlying cause.",
        "event_type": "System Instability",
        "requires_human_review": "true",
        "confidence_score": 0.8
      ,
        "recommended_actions": ["Monitor System Health", "Run Diagnostics", "Increase System Resources"]
      }
    ],
    "requires_immediate_attention": "true"
  }

  newobj={
    "summary": "The logs reveal a pattern of intermittent RAID array failures within the billing and legacy CRM systems. There are also multiple instances of security alerts indicating suspicious login attempts from various IP addresses, as well as warnings about deprecated features and the need to migrate to newer functionalities. The frequency of the RAID array issues and security alerts suggests a potential hardware or configuration problem that requires immediate investigation.",
    "observations": [
      "High frequency of RAID array failures (multiple instances), suggesting a hardware issue or configuration problem within the billing and legacy CRM systems.",
      "Recurring security alerts (suspicious login attempts from different IP addresses) indicate potential unauthorized access attempts. Investigation into user accounts and the source of these attempts is crucial.",
      "Frequent warnings about deprecated features ('ExportToCSV' and 'getCustomerDetails') signify the need for a migration strategy to avoid compatibility issues and ensure the continued functionality of the legacy systems.",
      "The logs exhibit a temporal pattern, with the most intensive activity occurring during the late morning hours (around 10:00-11:00 UTC), which may correlate with peak user activity.",
      "Frequent RAID array crashes: The repeated occurrences of RAID array failures strongly suggest a hardware issue that needs immediate investigation. This is impacting the availability of the 'billing' and 'legacycrm' applications."
    ],
    "planning": [
      "**Immediate Action:** Immediately investigate the RAID array failures - this is the highest priority. Engage hardware support to diagnose and resolve the underlying issue.  Implement redundant configurations if possible.",
      "**Security Investigation:** Conduct a thorough audit of user accounts, focusing on the IP addresses associated with the security alerts.  Review access logs and authentication mechanisms.",
      "**Deprecated Feature Migration:** Prioritize a migration plan for the 'ExportToCSV' feature, as it's nearing obsolescence. Assess the impact of migrating to 'fetchCustomerInfo'.",
      "**Log Monitoring Enhancement:** Increase the granularity of log monitoring, particularly for RAID array status and security events. Implement alerting thresholds to proactively detect issues.",
      "**Root Cause Analysis:** Perform a root cause analysis to determine the source of the RAID array failures – is it a specific server, a network configuration issue, or a software problem?"
    ],
    "security_events": [
      {
        "reasoning": "Multiple security alerts with varying IP addresses raise significant concern.  These could be legitimate access attempts or malicious attacks. Immediate investigation is required.",
        "event_type": "Security Alert",
        "requires_human_review": "true",
        "confidence_score": 0.8
      ,
        "recommended_actions": [
          "Investigate the source of the login attempts.",
          "Review user access controls and permissions.",
          "Implement multi-factor authentication."
        ]
      },
      {
        "reasoning": "The repeated RAID array failures indicate a serious hardware issue that needs immediate attention to prevent data loss and service disruption.",
        "event_type": "Hardware Failure",
        "requires_human_review": "true",
        "confidence_score": 0.9
      ,
        "recommended_actions":[
          "Engage hardware support for diagnostics and repair.",
          "Implement a robust backup and recovery strategy.",
          "Evaluate the RAID configuration for redundancy."
        ]
      },
      {
        "reasoning": "Warnings about deprecated features highlight the risk of incompatibility and potential service disruptions. Proactive migration is essential.",
        "event_type": "Deprecated Feature",
        "requires_human_review": "false",
        "confidence_score": 0.7
      ,
        "recommended_actions":[
          "Assess the impact of migrating to 'fetchCustomerInfo'."
          , "Plan for the necessary code changes"
        ]
      }
    ],
    "hardware_failure_events": [
      {
        "reasoning": "The frequent RAID array failures are a critical issue that directly impacts system availability and data integrity.  It's a high priority for resolution.",
        "event_type": "RAID Array Failure",
        "requires_human_review": "true",
        "confidence_score": 0.95
      ,
        "recommended_actions":[
          "Prioritize hardware support engagement.",
          "Review the RAID configuration for redundancy.",
          "Assess the underlying server infrastructure."
        ]
      }
    ],
    "requires_immediate_attention": "true"
  }

  await merge(masterobj, newobj, embedding_model)

  newobj={
      "summary": "The logs reveal a pattern of several events, primarily related to the 'legacycrm' application. There's a recurring issue with the 'ExportToCSV' feature being outdated, coupled with repeated instances of escalation rule failures and lead conversion issues. The application experiences frequent RAID array disk crashes.  Notably, there are multiple security alerts indicating unauthorized login attempts from various IP addresses, coupled with a general pattern of suspicious activity. The application appears to be experiencing significant instability related to its RAID array.",
      "observations": [
        "The 'ExportToCSV' feature is consistently flagged as outdated, suggesting a need for immediate migration to 'ExportToXLSX'.",
        "Escalation rule failures are commonplace, indicating a likely design flaw or misconfiguration within the 'legacycrm' application's workflow.",
        "Lead conversion failures are frequently reported, pointing to potential problems with the lead generation or qualification process.",
        "The RAID array is experiencing frequent disk crashes, which is a critical stability issue and needs immediate investigation.",
        "Multiple security alerts suggest a potential security breach or a compromised environment.  The alerts originate from diverse IP addresses, requiring further investigation to determine the scope and source of the activity.",
        "The application's stability is severely compromised due to the RAID array failures."
      ],
      "planning": [
        "Prioritize immediate investigation of the RAID array failures. Engage storage specialists for diagnosis and repair.",
        "Investigate and resolve the escalation rule failures.  This likely requires a review of the escalation workflow and potentially a redesign.",
        "Address the outdated 'ExportToCSV' feature.  Initiate the migration to 'ExportToXLSX' and provide user training.",
        "Conduct a thorough security audit to determine the source of the security alerts.  This includes reviewing logs, network traffic, and user activity.",
        "Implement enhanced monitoring and alerting for the RAID array to proactively detect and respond to potential failures.",
        "Consider a phased rollout of changes to minimize disruption to users."
      ],
      "security_events": [
        {
          "reasoning": "Multiple security alerts (from various IPs) indicate unauthorized access attempts. This is a high-priority concern and requires immediate investigation.",
          "event_type": "Security Breach - Unauthorized Login Attempts",
          "requires_human_review": "true",
          "confidence_score": 0.9,
          "recommended_actions": [
            "Immediately investigate the source IP addresses.",
            "Review user access logs for any unauthorized activity.",
            "Strengthen authentication mechanisms (e.g., multi-factor authentication).",
            "Investigate possible vulnerabilities that may have been exploited."
          ]
        },
        {
          "reasoning": "Repeated escalation rule failures suggest a problem with the escalation process itself, which could be related to a workflow bug or misconfiguration.",
          "event_type": "Workflow Issue - Escalation Rule Failure",
          "requires_human_review": "true",
          "confidence_score": 0.7,
          "recommended_actions": [
            "Review the escalation rule definitions and their associated logic.",
            "Test the escalation process to identify any potential triggers or bottlenecks.",
            "Validate the workflow steps and ensure they align with business requirements."
          ]
        },
        {
          "reasoning": "Frequent lead conversion failures highlight a potential issue with the lead generation or qualification process, indicating a flaw in the application's core functionality.",
          "event_type": "Operational Issue - Lead Conversion Failure",
          "requires_human_review": "true",
          "confidence_score": 0.6,
          "recommended_actions": [
            "Examine the lead generation process for potential bugs or misconfigurations.",
            "Evaluate the criteria used for lead qualification and ensure they align with business goals.",
            "Assess the impact of the lead conversion failures on overall sales performance."
          ]
        }
      ],
      "hardware_failure_events": [
        {
          "reasoning": "The repeated RAID array disk crashes represent a critical stability issue. This requires immediate action to prevent data loss and system downtime.",
          "event_type": "Hardware Failure - RAID Array Disk Crash",
          "requires_human_review": "true",
          "confidence_score": 0.95,
          "recommended_actions": [
            "Engage storage specialists for diagnosis and repair.",
            "Implement a robust RAID redundancy strategy.",
            "Establish a regular maintenance schedule for the RAID array."
          ]
        }
      ],
      "requires_immediate_attention": "true"
    }

  await merge(masterobj, newobj, embedding_model)

  newobj={
      "summary": "The logs reveal a pattern of intermittent issues, primarily related to RAID array failures and occasional suspicious activity, including unauthorized login attempts and unusual IP addresses. There's a clear trend of lead conversion failures linked to missing contact information, suggesting a potential problem with data synchronization or lead quality.  The application is experiencing frequent, albeit sporadic, errors, and the 'legacycrm' application is exhibiting a higher frequency of issues compared to the 'simpleapp'. The use of legacy authentication methods is a potential area of concern given the impending deprecation. The alert notifications indicate potential security breaches.",
      "observations": [
        "Frequent RAID array crashes: The repeated occurrences of RAID array failures strongly suggest a hardware issue that needs immediate investigation. This is impacting the availability of the 'billing' and 'legacycrm' applications.",
        "Lead Conversion Failures: A significant number of lead conversion failures, consistently linked to missing contact information, points to a problem with data integrity, potentially synchronization issues between systems, or a flawed lead generation process.",
        "Suspicious Activity: Multiple alerts indicating unauthorized login attempts from unusual IP addresses (10.2.4.5, 192.168.1.10, 172.135.223.12) are concerning and need thorough review.  These should be prioritized.",
        "Legacy Authentication: The continued use of legacy authentication methods presents a security risk given its planned deprecation. Migration to modern authentication is strongly recommended.",
        "Application Performance: The 'legacycrm' application appears to be more prone to errors compared to the 'simpleapp', suggesting potential issues with its design, configuration, or underlying infrastructure."
      ],
      "planning": [
        "**Immediate Action:** Initiate a hardware diagnostic on the RAID arrays. Schedule a technician to investigate and potentially replace failing drives.",
        "**Security Review:**  Immediately investigate the suspicious login attempts.  Analyze network traffic around the times of these attempts.  Implement stricter access controls and multi-factor authentication.",
        "**Data Integrity Check:** Investigate the source of the missing contact information during lead conversion failures. Verify data synchronization processes between systems.  Implement data validation checks.",
        "**Legacy Authentication Migration:** Develop a plan and timeline to migrate the 'legacycrm' application to a modern authentication system.",
        "**Performance Monitoring:** Implement more granular performance monitoring for the 'legacycrm' application to identify potential bottlenecks and performance issues.",
        "**Root Cause Analysis:** Perform a thorough root cause analysis of all errors to prevent recurrence."
      ],
      "security_events": [
        {
          "reasoning": "Multiple alerts for unauthorized login attempts from different IP addresses suggest a possible brute-force attack or account compromise. The alerts indicate a potential security breach and require immediate investigation.",
          "event_type": "Security Breach",
          "requires_human_review": "true",
          "confidence_score": 0.85
        ,
          "recommended_actions": ["Investigate network traffic logs", "Review user account activity", "Implement stronger authentication methods"]
        },
        {
          "reasoning": "Frequent RAID array failures are indicative of hardware problems. This could lead to data loss and application downtime.  The repeated failures suggest a systemic issue.",
          "event_type": "Hardware Failure",
          "requires_human_review": "true",
          "confidence_score": 0.9
        ,
          "recommended_actions": ["Schedule hardware diagnostic", "Replace failing drives"]
        },
        {
          "reasoning": "The accumulation of lead conversion failures with missing contact information likely indicates a fundamental problem in the lead generation or data synchronization process. It’s a symptom of a larger issue.",
          "event_type": "Data Integrity Issue",
          "requires_human_review": "true",
          "confidence_score": 0.75
        ,
          "recommended_actions": ["Review lead generation process", "Validate data synchronization processes", "Improve data quality"]
        }
      ],
      "hardware_failure_events": [
        {
          "reasoning": "The repeated RAID array failures point to a hardware problem that requires immediate attention. This is a critical system failure.",
          "event_type": "RAID Array Failure",
          "requires_human_review": "true",
          "confidence_score": 0.95
        ,
          "recommended_actions": ["Schedule hardware diagnostic", "Replace failing drives"]
        },
        {
          "reasoning": "The frequency of RAID array failures suggests a broader hardware issue within the system's storage infrastructure.",
          "event_type": "Storage Infrastructure Failure",
          "requires_human_review": "true",
          "confidence_score": 0.8
        ,
          "recommended_actions": ["Evaluate storage system health", "Consider storage system upgrade"]
        }
      ],
      "requires_immediate_attention": "true"
    }

  await merge(masterobj, newobj, embedding_model)

  await compress(masterobj)
  print(masterobj)




async def bigtest():
  MAX_TOKENS=4048
  MAX_SUMMARIES_BEFORE_COMPRESS=28
  embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
  file_path = "/workspaces/ai-lab/backend/aiapp/summarise-in-chunk-output-sample.txt"
  master_summary_obj={}
  for idx, obj in enumerate(read_json_objects(file_path), start=1):
      print(f"\n\nPROCESSING----->{idx}\n\n")
      if len(master_summary_obj) < 1:
        master_summary_obj = obj
      else:
        await merge(master_summary_obj, obj, embedding_model)
        print(master_summary_obj)
        if "summaries" in master_summary_obj and len(master_summary_obj["summaries"]) > MAX_SUMMARIES_BEFORE_COMPRESS:
          all_summary_text = "\n".join(f"\"{line}\"," for line in master_summary_obj["summaries"])
          est_summary_tokens = estimate_tokens(all_summary_text)
          print(f"summaries token: {est_summary_tokens}")
          if est_summary_tokens > MAX_TOKENS:
            await compress(master_summary_obj)
# Example usage
if __name__ == "__main__":
  asyncio.run(smalltest())
  


