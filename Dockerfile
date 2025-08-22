FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt aiohttp
COPY . .
ENV OUT_DIR=/app/data
# Seed initial data (skip failures in build without API key)
RUN python collector.py || true
EXPOSE 8080
CMD ["python","server.py"]
