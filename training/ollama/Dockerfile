FROM ollama/ollama:0.6.8 AS builder


WORKDIR /app

# Set environment variables to disable GPU (CPU mode)
# ENV OLLAMA_CUDA=0

COPY Modelfile.granite .
COPY Modelfile .
COPY granite-3.3-8b-instruct-Q4_K_M.gguf .
COPY ilab-trained-granite-7b-Q4_K_M.gguf .
COPY ollama-start.sh .
RUN chmod +x ollama-start.sh
# Mount a local directory containing your model
# VOLUME ["training/models:/app/models"]

# Expose the Ollama API port
EXPOSE 11434

WORKDIR /app

RUN apt-get update && apt-get install -y wget curl

RUN echo "Starting Ollama server in background..." \
    && ollama serve & \
    sleep 10 \
    && echo "Creating model from Modelfile..." \
    && sleep 3 \
    && ollama create ilab-trained-granite-7b -f Modelfile \
    && sleep 2 \
    && echo "Creating model from Modelfile.granite..." \
    && sleep 3 \
    && ollama create granite-3.3-8b-instruct -f Modelfile.granite \
    && sleep 2 \
    && echo "Listing models under ollama..." \
    && ollama list
    


# Stage 2: Create the final image
FROM ollama/ollama:0.6.8 

# Copy the model from the builder stage
COPY --from=builder /root/.ollama /root/.ollama

# Expose the Ollama API port
EXPOSE 11434

# Start the Ollama server when the container runs
ENTRYPOINT ["ollama"]
CMD ["serve"]

# RUN wget -q -O - https://ollama.com/install.sh | sh /dev/stdin

# RUN ollama create granite-3.3-2b-instruct -f Modelfile
# RUN ollama list
# RUN ollama serve & 
# RUN ollama create granite-3.3-2b-instruct -f Modelfile && sleep 5
# Start the Ollama server with the local model
# CMD ["ollama", "serve", "--model", "/app/granite-3.3-2b-instruct-Q4_K_M.gguf", "--port", "11434"]

# ENTRYPOINT ["/usr/local/bin/ollama"]
# CMD ["ollama", "serve"]
# docker build -t ollama-granite .
# docker run --rm -it -p 11434:11434 --name ollama-granite ollama-granite
# docker exec -it ollama-granite /bin/bash