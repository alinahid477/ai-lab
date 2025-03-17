from kafka import KafkaConsumer, TopicPartition
import json
import time
from datetime import datetime, timedelta
import pandas as pd
import os

def extract_kafka_logs(duration):
    kafkaBrokers = os.getenv("KAFKA_BROKER_ENDPOINT")
    caRootLocation='/certs/kafkabroker/ssl/CARoot.pem'
    certLocation='/certs/kafkabroker/ssl/certificate.pem'
    keyLocation='/certs/kafkabroker/ssl/key.pem'
    password=os.getenv("KAFKA_BROKER_SSL_PASSWORD")


    topic='ocplogs-myapp'
    consumer = KafkaConsumer(topic,
        bootstrap_servers=[kafkaBrokers],
        value_deserializer=lambda x: x.decode('utf-8'),
        security_protocol='SSL',
        ssl_check_hostname=False,
        ssl_cafile=caRootLocation,
        ssl_certfile=certLocation,
        # ssl_keyfile=keyLocation,
        ssl_password=password,
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        consumer_timeout_ms=180000 # 3 minutes
    )


    timestamp_duration_hrs_ago = int((datetime.now() - timedelta(hours=duration)).timestamp() * 1000)


    partitions = consumer.partitions_for_topic(topic)
    topic_partitions = [TopicPartition(topic, p) for p in partitions]

    # Get the offsets for the timestamp 24 hours ago
    offsets = consumer.offsets_for_times({tp: timestamp_duration_hrs_ago for tp in topic_partitions})

    # Seek to the calculated offsets
    for tp in topic_partitions:
        if offsets[tp] is not None:
            consumer.seek(tp, offsets[tp].offset)

    end_offsets = consumer.end_offsets(topic_partitions)

    data = []
    count=0
    for event in consumer:
        tp = TopicPartition(event.topic, event.partition)
        if event.offset >= end_offsets[tp]:
            break
        if count>100000:
            break
        msg = event.value
        if msg is None:
            print("Waiting...")
        else:
            obj = json.loads(msg)
            timestamp = obj.get('@timestamp', 'N/A')
            namespace_name = obj.get('kubernetes', {}).get('namespace_name', 'N/A')
            app_name = obj.get('kubernetes', {}).get('container_name', 'N/A')
            message = obj.get('message', 'N/A')
            if pd.isna(message) or message.startswith('\t'):
                continue
            level = obj.get('level', 'N/A')
            log_type = obj.get('log_type', 'N/A')
            data.append({
                'timestamp': timestamp,
                'namespace_name': namespace_name,
                'app_name': app_name,
                'level': level,
                'log_type': log_type,
                'message': message,
                # 'target_classification': '',
            })
            # print(f"Namespace: {namespace_name}, app: {app_name}, Level: {level}, Type: {log_type}, Message: |{message}|")
            # if app_name != 'kafka':
            #     # print(f"level: {level}, count: {count}")
            #     count = count + 0 # do nothing
            count+=1

        df = pd.DataFrame(data)

    filename = f"/tmp/myapp_logs_{duration}hrs_{datetime.now().strftime('%Y%m%d%H%M')}.csv"
    df.to_csv(filename, index=False)

    return filename


if __name__ == '__main__':
    extract_kafka_logs(24)