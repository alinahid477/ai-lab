


#### To increase content

add this line in the Modelfile
```
PARAMETER num_ctx 80072
```

```
docker build -t ollama-granite .

docker tag ollama-granite:latest quay.io/rh-ee-anahid/ollama-granite:v10
docker push quay.io/rh-ee-anahid/ollama-granite:v10

docker run --rm -it --name ollama-granite -p 11434:11434 ollama-granite
```