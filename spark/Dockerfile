FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends default-jre-headless \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN pip install --no-cache-dir pyspark==3.5.3 psycopg2-binary==2.9.9 prometheus_client==0.20.0
COPY jobs/clean_and_load.py .
CMD ["python", "clean_and_load.py"]
