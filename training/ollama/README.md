

#### get the trained granite model
I trained this model to extract specific commands and their associated params.
```
curl https://huggingface.co/alinahid477/ilab-trained-granite-7b-lab/resolve/main/ilab-trained-granite-7b-Q4_K_M.gguf?download=true
```

#### To increase content

add this line in the Modelfile
```
PARAMETER num_ctx 80072
```

```
docker build -t ollama-server .

docker tag ollama-server:latest quay.io/rh-ee-anahid/ollama-server:v1
docker push quay.io/rh-ee-anahid/ollama-server:v1

docker run --rm -it --name ollama-server -p 11434:11434 ollama-server
```