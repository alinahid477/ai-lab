import json
import utils
import asyncio
import re 
import getfromai02
from helpers import merge_log_summarization
import os
import server

async def send_message_to_ws(message):
  print(f"**sending to ws: {message}")
  try:
    utils.send_to_websocket_sync({"type": "terminalinfo", "data": message})
  except Exception as e:
    print("SMWS EXCEPTION")


async def testGetCommand():
  # await getfromai02.get_intended_command("get log for the past 24hour")
  await getfromai02.get_intended_command("your name is gemma. you are an AI assistant.")
  await getfromai02.get_intended_command("what is your name?")

async def testSummarize():
  # obj = await getfromai02.summarize_logs("/tmp/logs/classified_myappocp_202505210455.nogit.csv", "/tmp/logs/classified_myappocp_202505210455.nogit.json")
  # print("\n\n")
  # print(obj)
  obj = await server.summarize("/tmp/logs/classified_myappocp_202505210455.nogit.csv")
  print(obj)

# async def testMerge():
#   await smalltest()


async def testCompress():
  obj = {'summary': "Analysis of the provided log data reveals a pattern of recurring errors and warnings related to data export, authentication, and escalation rules. The logs primarily consist of errors and warnings related to the 'ExportToCSV' feature, authentication, and undefined escalation levels.  The system experienced repeated issues with RAID array disk crashes and authentication. The logs suggest a need for migration to a newer export format and a review of escalation rule configurations.", 'observations': ["**Frequent 'ExportToCSV' Errors:** The logs consistently indicate problems with the 'ExportToCSV' feature. This suggests a potential issue with the export process itself, possibly stemming from data formatting, file handling, or dependencies.", '**Authentication Issues:** Instances of authentication-related warnings and errors are observed, highlighting a possible weakness in the authentication mechanism. This could involve incorrect credentials, problems with the authentication server, or issues with the authentication protocol.', '**Escalation Rule Failures:** Several errors indicate that escalation rules are not being properly applied. This could result in delayed responses, incorrect routing of issues, or unresolved problems.', '**RAID Array Failures:** Repeated errors related to RAID array disk crashes suggest a hardware or storage system problem.  This requires investigation and potentially a hardware upgrade or maintenance.', "**Trend:** There's a consistent trend of problems related to data export and authentication, which warrants immediate attention.", "Frequent Escalation Rule Failures: Ticket IDs 1047, 3493, 4745, 8230 are repeatedly failing due to 'undefined escalation level'. This requires investigation into the escalation rule definitions and their associated configurations.", "Lead Follow-up Issues:  Lead follow-up processes (associated with lead IDs 2311, 4616, 8380, 9406, 9660, 1047, 4616, 8380) are frequently failing because 'next action' is missing. This suggests a problem with data integrity or lead assignment.", 'Security Alerts:  Multiple security alerts indicate unauthorized login attempts.  These should be investigated immediately to prevent further breaches.', 'Deprecated Authentication: Warnings about the legacy authentication method highlight a potential vulnerability.  Migration to a modern authentication system is recommended.', 'System Stability: While not explicitly stated, the frequent errors suggest some instability within the system. Further monitoring and troubleshooting might be needed.', 'Repeated RAID array disk crashes, indicating a critical system instability issue.', 'Escalation rule failures suggest potential problems with workflow or components.', 'Lead conversion failures may indicate issues with lead management or data.', 'API deprecation warning requiring code updates.', 'Need for proactive log monitoring and alerting.'], 'planning': ["**Investigate 'ExportToCSV' Issues:** Begin by analyzing the data associated with the 'ExportToCSV' errors. Determine the root cause – is it a bug in the export code, data formatting problems, or dependency issues?", '**Review Authentication Mechanism:** Investigate the authentication server and the authentication process. Ensure credentials are correct and the authentication protocol is functioning properly.', '**Review Escalation Rules:** Analyze the escalation rules to determine why they are failing.  Verify that the rules are correctly configured and that the necessary dependencies are in place.', '**Storage System Health:**  Monitor the health of the RAID array and storage system. Consider performing diagnostic tests and potentially replacing failing hardware.', "**Migration to Newer Export Format:**  Prioritize migrating to a newer export format to address the 'ExportToCSV' issues. This should be a short-term solution while the root cause is investigated.", '**Logging Enhancement:** Add more detailed logging to specifically pinpoint the source of errors and warnings.  Include timestamps, user IDs, and relevant data.', 'Investigate Escalation Rules: Review and correct the definitions of the failing escalation rules (IDs 1047, 3493, 4745, 8230).', "Data Integrity Check: Analyze the data associated with the failing lead follow-up processes to identify the root cause of the missing 'next action'.", 'Security Audit: Conduct a thorough security audit to address the unauthorized login attempts.', 'Authentication Migration: Plan and execute a migration to a modern authentication system.', 'System Monitoring: Implement robust system monitoring to detect and respond to future issues.', 'RAID array repair/replacement - Priority 1', 'Security audit and strengthening', 'Investigate escalation rule failures', 'Analyze lead conversion failures', 'Update code to use `fetchCustomerInfo`', 'Implement enhanced log monitoring and alerting'], 'security_events': [{'reasoning': 'The repeated security alerts related to authentication and login attempts suggest a potential vulnerability.  Investigate suspicious login activity and implement additional security measures.', 'event_type': 'Security Alert', 'requires_human_review': True, 'confidence_score': 0.8, 'recommended_actions': ['Review security logs for suspicious activity.', 'Implement multi-factor authentication.', 'Strengthen password policies.'], 'id': 1}], 'hardware_failure_events': [{'reasoning': 'Repeated RAID array disk crash errors indicate a hardware failure. ', 'event_type': 'Hardware Failure', 'requires_human_review': True, 'confidence_score': 0.9, 'recommended_actions': ['Run diagnostic tests on the RAID array.', 'Replace failing disks.', 'Evaluate RAID array redundancy configuration.'], 'id': 1}], 'requires_immediate_attention': True, 'summaries': ['The logs show a recurring pattern of errors related to escalation rule executions, missing next action for lead follow-up processes, and warnings about the deprecated legacy authentication method.  There are also intermittent security alerts indicating potential unauthorized login attempts.  The system seems to be experiencing stability issues and needs attention to the escalation rules and potentially the authentication system.', "The log data shows a consistent pattern of errors and alerts related to security and system stability. Here's a breakdown of the key observations:\n\n**1. Security Alerts:**\n*   There are frequent security alerts indicating unauthorized login attempts from external IPs (10.2.4.5 and 172.135.223.12). This strongly suggests a potential security breach or attempted intrusion.\n*   These alerts highlight the need for robust security measures, including intrusion detection systems, firewall configurations, and regular security audits.\n\n**2. System Instability & Errors:**\n*   **RAID Array Errors:** Repeated messages about RAID array disk crashes (approximately every 30-45 minutes during the log's duration). This is a critical issue that could lead to data loss or system downtime.  Immediate investigation and potentially RAID array replacement/repair are needed.\n*   **Escalation Rule Failures:** Several instances of escalation rule execution failures (Ticket IDs 7652, 5353, 1932, 1155, etc.).  These rules are likely part of a workflow for handling incidents, and their failure points to a problem in the workflow or a failing component.\n*   **Lead Conversion Failures:**  Several errors related to lead conversion failures (Ticket IDs 3066, 8474, 6938). This suggests issues with the lead management process or associated data.\n*   **API Deprecation:** A warning about the deprecation of `getCustomerDetails` API and the recommendation to use `fetchCustomerInfo`. This indicates the need to update code to align with changes in the API.\n\n**3. Workflow & Process Issues:**\n*    **Escalation Rule Failures**: Suggest a problem with the escalation workflow itself, or with the components involved in triggering the rules.\n*   **Lead Conversion Failures**: Points to possible data quality problems, or issues with the lead management/sales process.\n\n**Recommendations:**\n\n1.  **Immediate RAID Array Repair/Replacement:** This is the highest priority. Data loss is a significant risk.\n2.  **Investigate Security Alerts:** Determine the source IPs and the nature of the attempted intrusions. Implement or strengthen security measures.\n3.  **Troubleshoot Escalation Rule Failures:**  Examine the rules and their dependencies.  Check for bugs or misconfigurations.\n4.  **Review Lead Management Process:**  Investigate the cause of the lead conversion failures.  Assess data quality and workflow.\n5.  **Update Code:** Migrate to the new `fetchCustomerInfo` API.\n6.  **Log Monitoring:** Implement more granular log monitoring and alerting to proactively detect similar issues in the future.  Analyze logs to identify patterns and root causes.\n\nTo help me provide even more tailored recommendations, could you tell me:\n\n*   What type of system is this log from (e.g., web application, database server, cloud platform)?\n*   What technologies are involved (e.g., programming language, database, operating system)?\n*   Are there any known dependencies or integrations that might be affected?\n*   Can you share any error messages in more detail?  (e.g., The full error message from the RAID array crash)"]}
  await merge_log_summarization.compress(obj)
  print(obj)

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

  # asyncio.run(testSummarize())
  # asyncio.run(testCompress())
  # logs_csv_file_path = '/home/user/documents/classified_log.sometime-2025-03-15.file.nogit.csv'
  # givenfilename = os.path.basename(logs_csv_file_path)
  # givenfilename = os.path.splitext(givenfilename)[0]
  # givenfiledir = os.path.dirname(logs_csv_file_path)
  # jsonfilename=f"summary_of_{givenfilename}.json"
  # summarize_file= os.path.join(givenfiledir,jsonfilename)
  # print (summarize_file)
  # data = utils.get_json_from_file("/tmp/logs/sample-summarise-response.json")
  # print(data)
  asyncio.run(testSummarize())