# ai-lab


source myenv/bin/activate
pip install --no-cache-dir -r requirements.txt



```
cd backend/aiapp/
docker build -t backend-aiapp .
docker tag backend-aiapp:latest quay.io/rh-ee-anahid/backend-aiapp:v6
docker push quay.io/rh-ee-anahid/backend-aiapp:v6

cd ../../
docker run --rm -it  --name backend-aiapp   --env-file ${PWD}/backend/aiapp/.env   -v ${pwd}/models/myclassifier/1/log_classifier.onnx:/mnt/models/logclassifier/1/model.onnx  -v ${PWD}/training/samples:/tmp/logs  -p 8000:8000   backend-aiapp
```


```
cd backend/websocket/
docker build -t backend-wsserver .
docker tag backend-wsserver:latest quay.io/rh-ee-anahid/backend-wsserver:v6
docker push quay.io/rh-ee-anahid/backend-wsserver:v6
cd ../../
docker run --rm -it  --name backend-wsserver -p 8765:8765   backend-wsserver

```

```
cd frontend
docker build -t frontend-aiapp .
docker tag frontend-aiapp:latest quay.io/rh-ee-anahid/frontend-aiapp:v6
docker push quay.io/rh-ee-anahid/frontend-aiapp:v6
cd ../../
docker run --rm -it --name frontend-aiapp --env-file $(pwd)/.env -p 3000:3000  frontend-aiapp
```

```
docker compose up
```