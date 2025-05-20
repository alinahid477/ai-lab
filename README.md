# ai-lab


source myenv/bin/activate
pip install --no-cache-dir -r requirements.txt



```
cd backend/aiapp/
docker build -t backend-aiapp .
docker tag backend-aiapp:latest quay.io/rh-ee-anahid/backend-aiapp:v3
docker push quay.io/rh-ee-anahid/backend-aiapp:v3

cd ../../
docker run --rm -it  --name backend-aiapp   --env-file $(pwd)/backend/aiapp/.env   -v $(pwd)/models/myclassifier/1/log_classifier.onnx:/mnt/models/logclassifier/1/model.onnx   -p 8000:8000   backend-aiapp
```


```
cd backend/websocker/
docker build -t backend-wsserver .
cd ../../
docker run --rm -it  --name backend-wsserver -p 8765:8765   backend-wsserver
docker tag backend-wsserver:latest quay.io/rh-ee-anahid/backend-wsserver:v2
```

```
cd frontend
docker build -t frontend-aiapp .
docker tag frontend-aiapp:latest quay.io/rh-ee-anahid/frontend-aiapp:v3
docker push quay.io/rh-ee-anahid/frontend-aiapp:v3
cd ../../
docker run --rm -it --name frontend-aiapp --env-file $(pwd)/.env -p 3000:3000  frontend-aiapp
```

```
docker compose up
```