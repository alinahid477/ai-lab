import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import classification
import granite
import kafka_extractor

import utils
import asyncio
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
    await utils.send_to_websocket({"type": "terminalinfo", "data": message})

@app.get("/csvlogs")
async def get_csv_logs(filepath, page: int, rowcount: int):
    # http://localhost:8000/csvlogs?filepath=/tmp/myappocp_202503182148.csv&page=0&rowcount=20
    try:
        if page is None:
            page = 0
        if rowcount is None:
            rowcount = 100
        await utils.send_to_websocket({"type": "terminalinfo", "data": f"Requested for data from rows {page*rowcount}-{page*rowcount+rowcount} of file:{filepath}."})
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
async def classify_csv(csv_file_path):
    try:
        return classification.classify_and_display_from_csv(csv_file_path, 0, 100)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        print("Processed classifying logs")
        # # Clean up if the file was saved
        # if os.path.exists("output.csv"):
        #     os.remove("output.csv")

@app.get("/downloadfile")
async def download_file(filepath: str):
    try:
        if not os.path.exists(filepath):
            await utils.send_to_websocket({"type": "terminalinfo", "data": f"Requested file {filepath} not found"})    
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(filepath, media_type='text/csv')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/processcommand")
async def process_english_command(command: str):
    try:
        return granite.get_intended_command(command)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        print(f"Processed english command: {command}")