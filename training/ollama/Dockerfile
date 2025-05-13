FROM ollama/ollama:0.6.8


WORKDIR /app

# Set environment variables to disable GPU (CPU mode)
ENV OLLAMA_CUDA=0

COPY Modelfile.granite .
COPY Modelfile .
COPY granite-3.3-2b-instruct-Q4_K_M.gguf .
COPY pytorch_model-Q4_K_M.gguf .
COPY ollama-start.sh .
RUN chmod +x ollama-start.sh
# Mount a local directory containing your model
# VOLUME ["training/models:/app/models"]

# Expose the Ollama API port
EXPOSE 11434

WORKDIR /app

RUN apt-get update && apt-get install -y wget curl

# RUN wget -q -O - https://ollama.com/install.sh | sh /dev/stdin

# RUN ollama create granite-3.3-2b-instruct -f Modelfile
# RUN ollama list
# RUN ollama serve & 
# RUN ollama create granite-3.3-2b-instruct -f Modelfile && sleep 5
# Start the Ollama server with the local model
# CMD ["ollama", "serve", "--model", "/app/granite-3.3-2b-instruct-Q4_K_M.gguf", "--port", "11434"]

ENTRYPOINT ["./ollama-start.sh"]
# docker build -t ollama-granite .
# docker run --rm -it -p 11434:11434 --name ollama-granite ollama-granite
# docker exec -it ollama-granite /bin/bash