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
RUN pip install hdfs


# =========================
# Copy Spark batch code
# =========================
COPY spark-batch.py /opt/spark/app/spark-batch.py

# =========================
# Set working directory
# =========================
WORKDIR /opt/spark/app
