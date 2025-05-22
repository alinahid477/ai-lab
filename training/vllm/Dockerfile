# Base image with vLLM installed
FROM vllm/vllm-openai:latest

# Set environment variables
ENV MODEL_PATH=/models/mistral-7b-v0.1.Q4_K_M.gguf
ENV TOKENIZER=/models/mistral-7b-v0.1.Q4_K_M.gguf

# Create directory for the model
RUN mkdir -p /models

# Copy your local GGUF model into the container
# Ensure the GGUF model file is in the same directory as this Dockerfile
COPY mistral-7b-v0.1.Q4_K_M.gguf /models/

# Expose the default port
EXPOSE 8123

# Start the vLLM server when the container launches
# CMD ["python", "-m", "vllm.entrypoints.openai.api_server"]
# CMD ["python", "-m", "vllm.entrypoints.openai.api_server" "--device", "cpu", "--model", "/models/granite-3.3-8b-instruct-Q4_K_M.gguf", "--tokenizer", "ibm-granite/granite-3.3-8b-instruct", "--host", "0.0.0.0", "--port", "8123"]
ENTRYPOINT ["/bin/bash"]