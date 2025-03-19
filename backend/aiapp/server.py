import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

import classification

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
@app.get("/csvlogs")
async def get_csv_logs(filepath, page: int, rowcount: int):
    # http://localhost:8000/csvlogs?filepath=/tmp/myappocp_202503182148.csv&page=0&rowcount=20
    try:
        if page is None:
            page = 0
        if rowcount is None:
            rowcount = 20
        print(f"{filepath}---{page} -- {rowcount}")
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

@app.post("/classify/")
async def classify_logs(csv_file_path):
    try:
        # Read the uploaded CSV
        df = pd.read_csv(csv_file_path)
        if "app_name" not in df.columns or "message" not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must contain 'source' and 'message' columns.")

        # Perform classification
        df["classification"] = classification.classify(list(zip(df["app_name"], df["message"])))

        print("Dataframe:",df.to_dict())

        # Save the modified file
        output_file = "resources/output.csv"
        df.to_csv(output_file, index=False)
        print("File saved to output.csv")
        return FileResponse(output_file, media_type='text/csv')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        print("Processed classifying logs")
        # # Clean up if the file was saved
        # if os.path.exists("output.csv"):
        #     os.remove("output.csv")