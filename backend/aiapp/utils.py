import pandas as pd
import asyncio
import websockets
import os
import json

async def send_to_websocket(data):
    if isinstance(data, dict):
        data = json.dumps(data)
    wsurl=os.getenv("WS_ENDPOINT")
    print(f"{wsurl}--->{data}")
    async with websockets.connect(wsurl) as websocket:
        await websocket.send(data)
        print(f"message: {data} SENT TO: {wsurl}")


def display_logs (source, page, rowcount):
    if isinstance(source, pd.DataFrame):
        return display_logs_from_dataframe(source, page, rowcount)
        
    return display_logs_from_csv(source, page, rowcount)


def display_logs_from_dataframe(df, page, rowcount):
    if rowcount == -100:  # -100 will mean give me all rows
        dfittr = df.iterrows()
    else:
        dfittr = df.iloc[page*rowcount:page*rowcount + rowcount].iterrows()
    
    return get_json(dfittr, "dataframe", page, rowcount)

def display_logs_from_csv(filepath, page, rowcount):    
    if rowcount == -100: # -100 will mean give me all rows
        df = pd.read_csv(filepath)
        dfittr = df.iterrows()
    else:
        df = pd.read_csv(filepath, skiprows=page*rowcount)
        dfittr = df.head(rowcount).iterrows()
    
    return get_json(dfittr, filepath, page, rowcount)

def get_json(df_ittr, filepath, page, rowcount):
    result = {'filepath': filepath, 'page': page, 'rowcount': rowcount, 'data': []}
    for index, row in df_ittr:
        if index > rowcount:
            break
        result['data'].append({
            'timestamp': row['timestamp'],
            'namespace_name': row['namespace_name'],
            'app_name': row['app_name'],
            'level': row['level'],
            'log_type': row['log_type'],
            'message': row['message'],
        })

    return result

if __name__ == '__main__':
    ret = display_logs("/tmp/test.csv", 0, 100)
    print(ret)