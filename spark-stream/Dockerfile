# =========================
# Base image
# =========================
FROM apache/spark:3.5.5-java17-python3

# =========================
# Use root user
# =========================
USER root

# =========================
# Install system deps + pip
# =========================
RUN apt-get update && \
    apt-get install -y wget python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# =========================
# Install Python dependencies
# =========================
RUN pip install --no-cache-dir pymongo==4.15.5

# =========================
# Download Spark / Kafka / MongoDB JARs
# =========================
RUN mkdir -p /tmp/jars && \
    cd /tmp/jars && \
    rm -f *.jar && \
    \
    wget https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.0/spark-sql-kafka-0-10_2.12-3.5.0.jar && \
    wget https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.0/spark-token-provider-kafka-0-10_2.12-3.5.0.jar && \
    wget https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.4.1/kafka-clients-3.4.1.jar && \
    wget https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.2.0/mongo-spark-connector_2.12-10.2.0.jar && \
    wget https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-sync/4.11.1/mongodb-driver-sync-4.11.1.jar && \
    wget https://repo1.maven.org/maven2/org/mongodb/bson/4.11.1/bson-4.11.1.jar && \
    wget https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-core/4.11.1/mongodb-driver-core-4.11.1.jar && \
    wget https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar && \
    wget https://repo1.maven.org/maven2/org/lz4/lz4-java/1.8.0/lz4-java-1.8.0.jar && \
    wget https://repo1.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.10.3/snappy-java-1.1.10.3.jar && \
    \
    echo "Downloaded $(ls *.jar | wc -l) JARs" && \
    ls -lh

# =========================
# Copy Spark streaming code
# =========================
COPY spark-kafka-streaming.py /opt/spark/app/spark-kafka-streaming.py

# =========================
# Set working directory
# =========================
WORKDIR /opt/spark/app
