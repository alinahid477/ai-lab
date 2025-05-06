#!/bin/bash

#!/bin/bash

echo "Starting Ollama server in background..."
ollama serve &

sleep 1
# Wait until the API is responsive
count=0
until curl -s http://localhost:11434 > /dev/null; do
  if count > 15
  then
    break
  else
    ((count++)) 
  fi
  echo "Waiting for Ollama server to be ready..."
  sleep 1
done

echo "Creating model from Modelfile..." && sleep 3
ollama create granite-3.3-2b-instruct -f Modelfile

echo "Listing models under ollama..." && sleep 2
ollama list

sleep 2
echo "Running model: granite-3.3-2b-instruct..."
ollama run granite-3.3-2b-instruct

