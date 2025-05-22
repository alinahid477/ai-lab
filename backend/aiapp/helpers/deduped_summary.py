import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


def dedupe (masterArr, newArr, embedding_model):
  
  embedding_dim = embedding_model.get_sentence_embedding_dimension()

  # Initialize the FAISS index for inner product (cosine similarity)
  vector_db = faiss.IndexFlatIP(embedding_dim)
  
  for item in masterArr:
    embedding = embedding_model.encode([item])
    normalized_embedding = normalize(embedding)
    vector_db.add(normalized_embedding)  

  for item in newArr:
    isitsimilar=is_similar(item, vector_db, embedding_model)
    if isitsimilar == False:
       masterArr.append(item)
    else:
       print(item)

def dedupe_summarization_object (master_obj, new_obj, embedding_model):
  
  dedupe(master_obj["observations"], new_obj["observations"], embedding_model)
  # todo: if observation is more than 10 compress it into 5.
  dedupe(master_obj["planning"], new_obj["planning"], embedding_model)
  # todo: if planning is more than 10 compress it into 5.


  new_security_events = [
    event for event in new_obj["security_events"]
    if event["confidence_score"] > 0.95
  ]
  # Extract all reasoning texts
  new_reasonings = [event["reasoning"] for event in new_security_events]
  master_reasonings = [event["reasoning"] for event in master_obj["security_events"]]
  dedupe(master_reasonings, new_reasonings, embedding_model)
  uncommon_set = set(master_reasonings).symmetric_difference(new_reasonings)
  uncommon = list(uncommon_set)
  for event in new_obj["security_events"]:
     if event["reasoning"] in uncommon:
        master_obj["security_events"].append(event)

  

  new_hardware_events = [
    event for event in new_obj["hardware_failure_events"]
    if (event["confidence_score"] > 0.95 and event["confidence_score"] <= 1) or event["confidence_score"] > 95
  ]
  # Extract all reasoning texts
  new_reasonings = [event["reasoning"] for event in new_hardware_events]
  master_reasonings = [event["reasoning"] for event in master_obj["hardware_failure_events"]]
  dedupe(master_reasonings, new_reasonings, embedding_model)
  uncommon_set = set(master_reasonings).symmetric_difference(new_reasonings)
  uncommon = list(uncommon_set)
  for event in new_obj["hardware_failure_events"]:
     if event["reasoning"] in uncommon:
        master_obj["hardware_failure_events"].append(event)


# Normalize function for embeddings
def normalize(vector):
    return vector / np.linalg.norm(vector)

# Function to add event if it's unique
def is_similar(textItem, vector_db, embedding_model, threshold=0.85):
  embedding = embedding_model.encode([textItem])
  normalized_embedding = normalize(embedding)
  if vector_db.ntotal > 0:
      similarities, _ = vector_db.search(normalized_embedding, k=1)
      if similarities[0][0] >= threshold:
          # print("*****************")
          # print(f"Duplicate detected (similarity: {similarities[0][0]:.4f}). Skipping insertion.")
          # print("*****************")
          return True

  vector_db.add(normalized_embedding)
  return False
  
# Example usage
if __name__ == "__main__":
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

# Initialize the embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

dedupe_summarization_object(masterobj, newobj, embedding_model)

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

dedupe_summarization_object(masterobj, newobj, embedding_model)

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

dedupe_summarization_object(masterobj, newobj, embedding_model)

print(masterobj)


