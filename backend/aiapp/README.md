

```
export $(grep -v '^#' .env | xargs)
uvicorn server:app --reload
```



https://github.com/rh-aiservices-bu/llm-on-openshift/blob/main/llm-servers/ollama/README.md


https://medium.com/@yuxiaojian/host-your-own-ollama-service-in-a-cloud-kubernetes-k8s-cluster-c818ca84a055


https://medium.com/towards-generative-ai/efficient-inference-on-ibm-granite-model-with-vllm-4f79aa7a16d0
https://www.ibm.com/granite/docs/run/granite-with-vllm/containerized/

```
docker pull vllm/vllm-openai:latest

docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -p 8000:8000 \
    vllm/vllm-openai:latest \
    --model ibm-granite/granite-3.1-8b-instruct

curl -H "Content-Type: application/json" http://localhost:8000/v1/chat/completions -d '{
  "model": "ibm-granite/granite-3.1-2b-instruct",
  "messages": [
    {"role": "users", "content": "How are you today?"}
  ]
}'
```