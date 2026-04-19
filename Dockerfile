from python:3.11-slim

workdir /app

env pythonunbuffered=1 \
    pythonpath=/app

run apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

copy requirements.txt /app/requirements.txt
run pip install --no-cache-dir -r /app/requirements.txt

copy . /app

cmd ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]