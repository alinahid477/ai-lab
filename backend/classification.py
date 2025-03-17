import onnxruntime as ort
import numpy as np
from sentence_transformers import SentenceTransformer
import pandas as pd



def classify(csv_file):

    onnx_session = ort.InferenceSession("../models/myclassifier/1/log_classifier.onnx")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    test_df = pd.read_csv(csv_file)
    test_df['classification'] = ''


    for index, row in test_df.iterrows():
        test_log = row['message']
        test_embeddings = model.encode([test_log])
        test_inputs = {onnx_session.get_inputs()[0].name: test_embeddings.astype(np.float32)}
        # print(test_inputs) --> {'float_input': array([[ 0.00000000e+00,  0.00000000e+00,  0.00000000e+00, ...]], dtype=float32)}
        # print(onnx_session.get_inputs()[0]) --> NodeArg(name='float_input', type='tensor(float)', shape=[None, 384])
        test_probabilities = onnx_session.run(None, test_inputs)
        test_predicted_label = 'Unclassified'
        if(len(test_probabilities) < 2):
            probabilities_dict = test_probabilities[1][0]
            test_predicted_label = max(probabilities_dict, key=probabilities_dict.get)
            print(test_log, "--> Unclassified -->", test_predicted_label)
        else:
            test_predicted_label = test_probabilities[0][0]
            # print(test_log, "->", test_predicted_label, "-->", test_probabilities)
        test_df.at[index, 'classification'] = test_predicted_label

    test_df.to_csv('myapp_logs-test_with_classification.nogit.csv', index=False)


if __name__ == '__main__':
    classify("test.csv")
    # logs = [
    #     ("ModernCRM", "IP 192.168.133.114 blocked due to potential attack"),
    #     ("BillingSystem", "User 12345 logged in."),
    #     ("AnalyticsEngine", "File data_6957.csv uploaded successfully by user User265."),
    #     ("AnalyticsEngine", "Backup completed successfully."),
    #     ("ModernHR", "GET /v2/54fadb412c4e40cdbaed9335e4c35a9e/servers/detail HTTP/1.1 RCODE  200 len: 1583 time: 0.1878400"),
    #     ("ModernHR", "Admin access escalation detected for user 9429"),
    #     ("LegacyCRM", "Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active."),
    #     ("LegacyCRM", "Invoice generation process aborted for order ID 8910 due to invalid tax calculation module."),
    #     ("LegacyCRM", "The 'BulkEmailSender' feature is no longer supported. Use 'EmailCampaignManager' for improved functionality."),
    #     ("LegacyCRM", " The 'ReportGenerator' module will be retired in version 4.0. Please migrate to the 'AdvancedAnalyticsSuite' by Dec 2025")
    # ]
    # labels = classify(logs)
    #
    # for log, label in zip(logs, labels):
    #     print(log[0], "->", label)