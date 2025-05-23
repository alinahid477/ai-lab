from kafka import KafkaConsumer, TopicPartition
import json
from datetime import datetime, timedelta
import pandas as pd
import os
import utils
import asyncio

async def send_message_to_ws(message):
    print(message)
    utils.send_to_websocket_sync({"type": "terminalinfo", "data": message})

async def get_logs(topic, duration):
    if duration not in [1, 2, 4, 6, 12, 24, 48, 72, 168]:
        await send_message_to_ws(f"STATUS: ERROR [500] Requested duration: {duration}. Duration must be one of the following values: 1, 2, 4, 6, 12, 24, 48, 72 hours.")
        raise Exception(f"Requested duration: {duration}. Duration must be one of the following values: 1, 2, 4, 6, 12, 24, 48, 72 hours.")
    if topic is None: 
        await  send_message_to_ws(f"STATUS: ERROR [500] Empty topic supplied. Must provide valid topic.")
        raise Exception("Empty topic supplied. Must provide valid topic.")    

    kafkaBrokers = os.getenv("KAFKA_BROKER_ENDPOINT")
    useSSL = os.getenv("KAFKA_USE_SSL", "false").lower() in ("true", "1", "yes")
    caRootLocation='/aiapp/certs/kafkabroker/ssl/CARoot.pem'
    certLocation='/aiapp/certs/kafkabroker/ssl/certificate.pem'
    keyLocation='/aiapp/certs/kafkabroker/ssl/key.pem'
    password=os.getenv("KAFKA_BROKER_SSL_PASSWORD")

    await send_message_to_ws(f"getting logs for the past: {duration}hrs for topic: {topic}")
    await send_message_to_ws(f"kafka broker: {kafkaBrokers}, ssl: {useSSL}, pass: {password}")

    
    if useSSL:
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
    else:
        consumer = KafkaConsumer(topic,
            bootstrap_servers=[kafkaBrokers],
            value_deserializer=lambda x: x.decode('utf-8'),
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
    await send_message_to_ws(f"received total: {len(df)} logs")
    return df





async def dataframe_to_csv (df, fileprefix):
    filename = f"/tmp/logs/{fileprefix}_{datetime.now().strftime('%Y%m%d%H%M')}.csv"
    await send_message_to_ws(f"Saving logs to file: {filename}")
    df.to_csv(filename, index=False)
    await send_message_to_ws(f"file {filename} saved successfully.")
    try:
        utils.cleanup()
    except Exception as e:
        print(f"Cleanup exception: {e}")
    return {"filename": filename}


async def getcsv_and_display(topic, duration, fileprefix, page, rowcount):
    await send_message_to_ws(f"Received request to retrieve logs from Kafka on topic: {topic} for the last {duration}hrs.")
    df = await get_logs(topic, duration)
    await send_message_to_ws(f"Saving logs to CSV file...")
    csv = await dataframe_to_csv(df, fileprefix)
    if page is None:
        page = 0
    if rowcount is None:
        rowcount = 100
    data = utils.display_logs(csv['filename'], page, rowcount)
    await send_message_to_ws(f"Respond back with rows: {page*rowcount} - {page*rowcount + rowcount}.")
    return data


async def getdata_and_display(topic, duration, page, rowcount):
    await send_message_to_ws(f"Received request to retrieve logs from Kafka on topic: {topic} for the last {duration}hrs.")
    df = await get_logs(topic, duration)
    if page is None:
        page = 0
    if rowcount is None:
        rowcount = 100
    await send_message_to_ws(f"Respond back with rows: {page*rowcount} - {page*rowcount + rowcount}.")
    return utils.display_logs(df, page, rowcount)
        

if __name__ == '__main__':
    ret = getdata_and_display("ocplogs-myapp", 1, None, None)
    print(ret)