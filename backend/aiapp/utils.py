import pandas as pd
import websockets
import os
import json
from websocket import create_connection
import glob
import time
from datetime import datetime, timedelta

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
    print(f"utils: Sending to ws: {data}")
    ws.send(data)
    # print(f"Message sent: {data}")
    # ws.close()
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
        dfittr = (df.iloc[page*rowcount:page*rowcount + rowcount].reset_index(drop=True)).iterrows()
    jsonData = get_json(dfittr, "dataframe", page, rowcount)
    jsonData['totalrow'] = len(df)
    send_to_websocket_sync({"type": "terminalinfo", "data": f"Displaying from {page*rowcount} to {page*rowcount + rowcount} of {jsonData['totalrow']}"})
    return jsonData

def display_logs_from_csv(filepath, page, rowcount):
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"The file {filepath} does not exist.")
        df = pd.read_csv(filepath)
        totalrow = len (df) 
        send_to_websocket_sync({"type": "terminalinfo", "data": f"Reading data from file:{filepath}..total_row:{totalrow}."})
        if rowcount == -100: # -100 will mean give me all rows    
            dfittr = df.iterrows()
        else:
            skip = page*rowcount
            if "classification" in df.columns:
                df = pd.read_csv(filepath, skiprows=skip, names=["timestamp", "namespace_name","app_name","level","log_type","message", "classification"])
            else:
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

def dataframe_to_csv(df, filesuffix, fileprefix="classified"):
    dir=os.path.dirname(filesuffix)
    if dir is None or dir == "": 
        dir="/tmp/logs"
        filename = f"{fileprefix}_{filesuffix}_{datetime.now().strftime('%Y%m%d%H%M')}.csv"
    else: # this means I have provided the original unclassified csv file fullpath 
        filename = f"{fileprefix}_{os.path.basename(filesuffix)}"
    
    classified_file = os.path.join(dir, filename)
    df.to_csv(classified_file, index=False)
    
    return {"filename": classified_file}


def truncate_csv(filepath, totalrows, skiprows):
    send_to_websocket_sync({"type": "terminalinfo", "data": f"truncating CSV: {filepath} to rows {totalrows}"})
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"The file {filepath} does not exist.")
        trows=int(totalrows)
        skip=0
        if skiprows:
            skip=int(skiprows)
        if skip > 0:
            df = pd.read_csv(filepath).head(2)
            if "classification" in df.columns:
                df = pd.read_csv(filepath, nrows=trows, names=["timestamp", "namespace_name","app_name","level","log_type","message", "classification"])
            else:
                df = pd.read_csv(filepath, nrows=trows, names=["timestamp", "namespace_name","app_name","level","log_type","message"])
            # this grabs labels for rows 1,2,…,200
            to_skip = df.index[:skip]       
            df2     = df.drop(index=to_skip)
            # If you want to re‐number your remaining rows from 0 upward:
            df = df2.reset_index(drop=True)
        else:
            df = pd.read_csv(filepath, nrows=trows)
        send_to_websocket_sync({"type": "terminalinfo", "data": f"Truncated: {filepath} to: {trows}"})
        csv = dataframe_to_csv(df, filepath, "truncated")
        jsonData = display_logs_from_dataframe(df, 0, 100)
        jsonData['filepath'] = csv["filename"]
        return jsonData
    except Exception as e:
        send_to_websocket_sync({"type": "terminalinfo", "data": f"Error reading data from file: {filepath}. Exception: {e}"})
        return {"error": f"Failed to truncate file: {filepath}. Exception: {e}"}

def listfiles():
  # Set the directory and the max allowed files
  log_dir = "/tmp/logs"
  max_files = 15

  # Get a list of all files in the directory
  files = glob.glob(os.path.join(log_dir, '*'))

  # Sort files by creation time in descending order
  files_sorted = sorted(files, key=os.path.getctime, reverse=True)
  return files_sorted  


def cleanup():
  
  # Set the directory and the max allowed files
	log_dir = "/tmp/logs"
	max_files = 15
  
	print(f"File cleanup starting....dir:{log_dir}, max_file_count: {max_files}")
  
	# Get a list of all files in the directory
	files = glob.glob(os.path.join(log_dir, '*'))

	# Only proceed if the number of files exceeds the max
	if len(files) > max_files:
			# Sort files by modification time (oldest first)
			files.sort(key=os.path.getmtime)

			# Determine how many files to delete
			files_to_delete = files[:len(files) - max_files]
			count=0
			for file_path in files_to_delete:
					if(count > 16):
							break
					else:
							count =+ 1
					try:
							os.remove(file_path)
							print(f"Deleted: {file_path}")
					except Exception as e:
							print(f"Failed to delete {file_path}: {e}")
	print(f"File cleanup ended....")


def get_json_from_file(filename):
  try:
    with open(os.path.join("/tmp/logs",filename), 'r') as json_file:
      data = json.load(json_file)
      return data
  except Exception as e:
    send_to_websocket_sync(f"EXCEPTION: executing get_json_from_file({filename}): ${e}")


if __name__ == '__main__':
    ret = display_logs("/tmp/test.csv", 0, 100)
    print(ret)