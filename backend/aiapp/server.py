import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import classification
import getfromai02
import kafka_extractor
import asyncio
import utils
from fastapi.middleware.cors import CORSMiddleware
import math
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


def sanitize_for_fastapi(obj):
    if isinstance(obj, float) and not math.isfinite(obj):
        return None
    if isinstance(obj, dict):
        return {k: sanitize_for_fastapi(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_for_fastapi(v) for v in obj]
    return obj

@app.get("/healthz")
async def healthz():
    return {"running": "ok"}

@app.get("/jsonsummary")
async def get_json_summary(filepath):
    return utils.get_json_from_file(filepath)

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
        sanitized_data = sanitize_for_fastapi(data)
        return sanitized_data
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
        givenfilename = os.path.basename(filepath)
        givenfilename = os.path.splitext(givenfilename)[0]
        givenfiledir = os.path.dirname(filepath)
        jsonfilename=f"summary_of_{givenfilename}.json"
        summarize_file= os.path.join(givenfiledir,jsonfilename)
        asyncio.create_task(_threaded_summarize(filepath, summarize_file))
        return {"message": {f"AI is working to generate summarization. It will be avaiable in file: {summarize_file}"}, "filename": summarize_file}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        print("Processed summarizing logs")


async def _threaded_summarize(filepath: str, summarize_file: str):
    # run the entire async function inside a new event‐loop in a thread
    def blocking_entry():
        import asyncio as _asyncio
        loop = _asyncio.new_event_loop()
        _asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(getfromai02.summarize_logs(filepath, summarize_file))
        finally:
            loop.close()

    try:
        await asyncio.to_thread(blocking_entry)
    except Exception as e:
        print(f"❌ Error in background threaded summarization of {filepath!r}: {e}")


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


# === Entry point ===
if __name__ == "__main__":
    # Launch FastAPI HTTP + WS server
    import uvicorn
    webport=int(os.getenv("BACKEND_SERVER_PORT", "8000"))
    webhost=(os.getenv("BACKEND_SERVER_HOST", "0.0.0.0"))
    print(f"Starting uvicorn on port {webhost}:{webport}...")
    uvicorn.run(app, host=webhost, port=webport)