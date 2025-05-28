FROM python:3.9-slim

WORKDIR /app

COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080 8081

CMD ["python", "-u", "proxy.py"]