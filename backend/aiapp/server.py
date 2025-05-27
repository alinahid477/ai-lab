import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import classification
import getfromai02
import kafka_extractor

import utils
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


async def send_message_to_ws(message):
    utils.send_to_websocket_sync({"type": "terminalinfo", "data": message})

@app.get("/jsonsummary")
async def get_json_summary(filename):
    return utils.get_json_from_file(filename)

@app.get("/csvlogs")
async def get_csv_logs(filepath, page: int, rowcount: int):
    # http://localhost:8000/csvlogs?filepath=/tmp/myappocp_202503182148.csv&page=0&rowcount=20
    try:
        if page is None:
            page = 0
        if rowcount is None:
            rowcount = 100
        utils.send_to_websocket_sync({"type": "terminalinfo", "data": f"Requested for data from rows {page*rowcount}-{page*rowcount+rowcount} of file:{filepath}."})
        # send_message_to_ws(f"Requested for data from rows {page*rowcount}-{page*rowcount+rowcount} of file:{filepath}.")
        data = utils.display_logs(filepath, page, rowcount)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/getapplogs")
async def get_app_logs(duration: int):
    try:
        return await kafka_extractor.getcsv_and_display("ocplogs-myapp", duration, "myappocp", 0, 30)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/classifycsv")
async def classify_csv(filepath):
    try:
        return classification.classify_and_display_from_csv(filepath, 0, 100)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        print("Processed classifying logs")
        # # Clean up if the file was saved
        # if os.path.exists("output.csv"):
        #     os.remove("output.csv")

@app.get("/summarize")
async def summarize(filepath):
    try:
        print(f" DEBUG 111 {filepath}")
        return await getfromai02.summarize_logs(filepath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        print("Processed summarizing logs")

@app.get("/downloadfile")
async def download_file(filepath: str):
    try:
        if not os.path.exists(filepath):
            utils.send_to_websocket_sync({"type": "terminalinfo", "data": f"Requested file {filepath} not found"})    
            raise HTTPException(status_code=404, detail="File not found")
        print(f"DOWNALOAD FILE: {filepath}")
        return FileResponse(filepath, media_type='text/csv')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/processcommand")
async def process_english_command(command: str):
    try:
        print(f"Process english: {command}")
        return await getfromai02.get_intended_command(command)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        print(f"Processed english command: {command}")


@app.get("/listfiles")
async def list_files():
    try:
        files = utils.listfiles()
        print(f"FILES: {files}")
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        print("Processed listing files in /tmp/logs dir")

@app.get("/truncatecsv")
async def truncate_csv(filepath, totalrows, skiprows=0):
    try:
        send_message_to_ws(f"Processing truncating csv {filepath} to {totalrows} rows")
        print(f"Processing truncating csv {filepath} to {totalrows} rows...")
        json = utils.truncate_csv(filepath, totalrows, skiprows)
        return json
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        send_message_to_ws(f"Processed truncating csv {filepath} to {totalrows} rows")