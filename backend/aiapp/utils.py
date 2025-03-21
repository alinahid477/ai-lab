import pandas as pd
import asyncio
import websockets
import os
import json
from websocket import create_connection


async def send_to_websocket(data):
    try:
        if isinstance(data, dict):
            data = json.dumps(data)
        wsurl=os.getenv("WS_ENDPOINT")
        # print(f"{wsurl}--->{data}")
        async with websockets.connect(wsurl) as websocket:
            await websocket.send(data)
            # print(f"message: {data} SENT TO: {wsurl}")
    except Exception as e:
        print(f"Error sending data to websocket: {e}")

def send_to_websocket_sync(data):
    try:
        if isinstance(data, dict):
            data = json.dumps(data)
        wsurl = os.getenv("WS_ENDPOINT")
        
        
        # Create a synchronous WebSocket connection
        ws = create_connection(wsurl)
        ws.send(data)
        # print(f"Message sent: {data}")
        ws.close()
    except Exception as e:
        print(f"Error sending data to WebSocket: {e}")


def display_logs (source, page, rowcount):
    if isinstance(source, pd.DataFrame):
        return display_logs_from_dataframe(source, page, rowcount)
    return display_logs_from_csv(source, page, rowcount)


def display_logs_from_dataframe(df, page, rowcount):
    if rowcount == -100:  # -100 will mean give me all rows
        dfittr = df.iterrows()
    else:
        dfittr = df.iloc[page*rowcount:page*rowcount + rowcount].iterrows()
    
    jsonData = get_json(dfittr, "dataframe", page, rowcount)
    jsonData['totalrow'] = len(df)
    return jsonData

def display_logs_from_csv(filepath, page, rowcount):
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"The file {filepath} does not exist.")
        df = pd.read_csv(filepath)
        totalrow = len (df) 
        send_to_websocket_sync({"type": "terminalinfo", "data": f"Reading data from file:{filepath}."})
        if rowcount == -100: # -100 will mean give me all rows    
            dfittr = df.iterrows()
        else:
            skip = page*rowcount        
            df = pd.read_csv(filepath, skiprows=skip, names=["timestamp", "namespace_name","app_name","level","log_type","message"])
            dfittr = df.head(rowcount).iterrows()
        jsonData = get_json(dfittr, filepath, page, rowcount)
        jsonData['totalrow'] = totalrow
        return jsonData
    except Exception as e:
        send_to_websocket_sync({"type": "terminalinfo", "data": f"Error reading data from file: {filepath}. Exception: {e}"})
        return {"error": f"Failed to read data from file: {filepath}. Exception: {e}"}


def get_json(df_ittr, filepath, page, rowcount):
    send_to_websocket_sync({"type": "terminalinfo", "data": f"Preparing data for display"})
    result = {'filepath': filepath, 'page': page, 'rowcount': rowcount, 'data': []}
    for index, row in df_ittr:
        if index > rowcount:
            break
        classification = "N/A"
        if 'classification' in row:
            classification = row['classification']
        try:
            result['data'].append({
                'timestamp': row['timestamp'],
                'namespace_name': row['namespace_name'],
                'app_name': row['app_name'],
                'level': row['level'],
                'log_type': row['log_type'],
                'message': row['message'],
                'classification': classification          
            })

        except Exception as e:
            print(f"Error processing row {index}: {e}")
    return result

if __name__ == '__main__':
    ret = display_logs("/tmp/test.csv", 0, 100)
    print(ret)