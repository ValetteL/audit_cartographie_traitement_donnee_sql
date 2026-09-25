FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install --no-cache-dir docker==7.1.0 prometheus_client==0.20.0
COPY exporter.py .
CMD ["python", "exporter.py"]
