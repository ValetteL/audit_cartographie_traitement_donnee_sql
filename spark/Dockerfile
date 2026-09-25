FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends default-jre-headless \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN pip install --no-cache-dir pyspark==3.5.3 psycopg2-binary==2.9.9 prometheus_client==0.20.0

# Fige le connecteur Kafka de Spark Structured Streaming dans l'image au build
# (résolution Maven via Ivy, une fois, pendant `docker compose build`) plutôt
# que de le télécharger à chaque démarrage via `spark.jars.packages` : aucun
# accès réseau requis ensuite au `docker compose up -d`.
RUN python -c "from pyspark.sql import SparkSession; \
SparkSession.builder.master('local[1]').appName('warm-ivy-cache') \
.config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3') \
.getOrCreate().stop()" \
    && cp /root/.ivy2/jars/*.jar /usr/local/lib/python3.11/site-packages/pyspark/jars/ \
    && rm -rf /root/.ivy2

COPY jobs/clean_and_load.py .
CMD ["python", "clean_and_load.py"]
