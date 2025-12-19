FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy app code
COPY app/ ./app/
COPY engine/ ./engine/
COPY middleware/ ./middleware/

# create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# expose ports
EXPOSE 8000 9090

# start the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]