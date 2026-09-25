FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install --no-cache-dir kafka-python==2.0.2 prometheus_client==0.20.0
COPY producer.py .
CMD ["python", "producer.py"]
