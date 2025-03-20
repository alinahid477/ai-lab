import pandas as pd
import asyncio
import websockets
import os
import json

async def send_to_websocket(data):
    if isinstance(data, dict):
        data = json.dumps(data)
    wsurl=os.getenv("WS_ENDPOINT")
    # print(f"{wsurl}--->{data}")
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
    
    jsonData = get_json(dfittr, "dataframe", page, rowcount)
    jsonData['totalrow'] = len(df)
    return jsonData

def display_logs_from_csv(filepath, page, rowcount): 
    if rowcount == -100: # -100 will mean give me all rows
        df = pd.read_csv(filepath)
        dfittr = df.iterrows()
    else:
        skip = page*rowcount
        print(f"{page}---{rowcount}--{skip}---{len(df)}")
        
        df = pd.read_csv(filepath, skiprows=skip, names=["timestamp", "namespace_name","app_name","level","log_type","message"])
        dfittr = df.head(rowcount).iterrows()
    jsonData = get_json(dfittr, filepath, page, rowcount)
    jsonData['totalrow'] = len(df)
    return jsonData


def get_json(df_ittr, filepath, page, rowcount):
    result = {'filepath': filepath, 'page': page, 'rowcount': rowcount, 'data': []}
    for index, row in df_ittr:
        if index > rowcount:
            break
        print (f"debug 4")
        print (f"debug 5: {index} {row['app_name']}")
        print (f"debug 6")
        try:
            result['data'].append({
                'timestamp': row['timestamp'],
                'namespace_name': row['namespace_name'],
                'app_name': row['app_name'],
                'level': row['level'],
                'log_type': row['log_type'],
                'message': row['message'],
            })

        except Exception as e:
            print(f"Error processing row {index}: {e}")
    return result

if __name__ == '__main__':
    ret = display_logs("/tmp/test.csv", 0, 100)
    print(ret)