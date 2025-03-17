import pandas as pd
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse





from backend.classification import classify

from backend.kafka_extractor import extract_kafka_logs

app = FastAPI()


async def get_logs_from_kafka(duration):
    if duration != 12 or duration != 24 or duration != 48:
        raise HTTPException(status_code=400, detail="Duration must be 12, 24, or 48 hours.")
    
    csv_file = extract_kafka_logs(duration)
    
    

@app.post("/classify/")
async def classify_logs(csv_file_path):
    try:
        # Read the uploaded CSV
        df = pd.read_csv(csv_file_path)
        if "app_name" not in df.columns or "message" not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must contain 'source' and 'message' columns.")

        # Perform classification
        df["classification"] = classify(list(zip(df["app_name"], df["message"])))

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