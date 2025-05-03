FROM ollama/ollama


WORKDIR /app

# Set environment variables to disable GPU (CPU mode)
ENV OLLAMA_CUDA=0

COPY Modelfile .
COPY granite-3.3-2b-instruct-Q4_K_M.gguf .
COPY ollama-start.sh .
RUN chmod +x ollama-start.sh
# Mount a local directory containing your model
# VOLUME ["training/models:/app/models"]

RUN ls -la /app

# Expose the Ollama API port
EXPOSE 11434


# RUN ollama create granite-3.3-2b-instruct -f Modelfile
# RUN ollama list

# Start the Ollama server with the local model
# CMD ["ollama", "serve", "--model", "/app/granite-3.3-2b-instruct-Q4_K_M.gguf", "--port", "11434"]
# CMD ["./ollama-start.sh"]
ENTRYPOINT ["./ollama-start.sh"]

# docker build -t ollama-granite .
# docker run --rm -it -p 11434:11434 ollama-granite --name ollama-granite