# ai-lab


source myenv/bin/activate
pip install --no-cache-dir -r requirements.txt



```
cd backend/aiapp/
docker build -t backend-aiapp .
cd ../../
docker run --rm -it  --name backend-aiapp   --env-file $(pwd)/backend/aiapp/.env   -v $(pwd)/models/myclassifier/1/log_classifier.onnx:/mnt/models/logclassifier/1/model.onnx   -p 8000:8000   backend-aiapp
```


```
cd backend/websocker/
docker build -t backend-wsserver .
cd ../../
docker run --rm -it  --name backend-wsserver -p 8765:8765   backend-wsserver
```

```
cd frontend
docker build -t frontend-aiapp .
cd ../../
docker run --rm -it --name frontend-aiapp --env-file $(pwd)/.env -p 3000:3000  frontend-aiapp
```
