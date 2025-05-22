import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Initialize the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')
embedding_dim = model.get_sentence_embedding_dimension()

# Initialize the FAISS index for inner product (cosine similarity)
index = faiss.IndexFlatIP(embedding_dim)

# Normalize function for embeddings
def normalize(vector):
    return vector / np.linalg.norm(vector)

# Function to add event if it's unique
def add_event_if_unique(event_text, threshold=0.85):
    embedding = model.encode([event_text])
    normalized_embedding = normalize(embedding)
    print("\n\n")
    print(f"processing....{event_text}")
    if index.ntotal > 0:
        similarities, _ = index.search(normalized_embedding, k=1)
        print(similarities[0][0])
        if similarities[0][0] >= threshold:
            print("*****************")
            print(f"Duplicate detected (similarity: {similarities[0][0]:.4f}). Skipping insertion.")
            print("*****************")
            return

    index.add(normalized_embedding)
    print("================")
    print(f"Event added to the index")
    print("================")
# Example usage
if __name__ == "__main__":
    # events = [
    #     "The frequent use of the deprecated 'getCustomerDetails' API endpoint is a significant concern. The system should be migrated to the 'fetchCustomerInfo' endpoint as soon as possible to avoid future deprecation issues.",
    #     "High frequency of deprecated feature warnings (getCustomerDetails and ExportToCSV) indicates a need for immediate migration to the recommended 'fetchCustomerInfo' endpoint and migration away from the outdated ExportToCSV feature.",
    #     "Repeated warnings about the deprecated 'getCustomerDetails' API.  Migration to 'fetchCustomerInfo' is critical, but the warnings highlight a significant operational risk.",
    #     "The deprecation of API endpoints (getCustomerDetails) should be actively addressed by migrating to the recommended 'fetchCustomerInfo' endpoint. This will prevent future issues and maintain system compatibility.",
    #     "The consistent warnings about the deprecated 'getCustomerDetails' API endpoint indicate a potential vulnerability if the system continues to rely on this endpoint.  Migration to 'fetchCustomerInfo' is critical.",
    #     "A high frequency of security alerts, particularly those indicating unauthorized login attempts from external IP addresses (172.135.223.12, 192.168.220.110, 10.2.4.5) suggests a potential brute-force attack or compromised credentials. The alerts are occurring during off-peak hours, which is atypical."  # Duplicate
    # ]
    # events = [
    #     "The recurring RAID array disk crash events (multiple instances) strongly suggest a hardware problem that needs immediate investigation. This is a major stability concern.",
    #     "RAID array failures are occurring regularly, indicating a potential hardware problem. Immediate investigation and repair are crucial to prevent data loss.",
    #     "High frequency of RAID array failures (multiple instances), suggesting a hardware issue or configuration problem within the billing and legacy CRM systems.",
    #     "Recurring RAID array failures suggest hardware instability, requiring hardware diagnostics and potentially a replacement.",
    #     "Recurring RAID array disk crashes, pointing to a hardware issue that requires immediate investigation and potentially replacement.",
    # ]

    events = [
        "The recurring RAID array disk crashes are a critical hardware failure. These failures can result in severe data loss and downtime if not addressed promptly.",
        "The RAID array disk crash messages indicate a critical hardware issue that has already impacted the system multiple times. Preventive replacement is essential."
    ]

    for event in events:
        add_event_if_unique(event)