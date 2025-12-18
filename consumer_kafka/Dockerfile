FROM python:3.9-slim

# Thiết lập thư mục làm việc và quyền root để cài đặt
WORKDIR /app
USER root

# Cài đặt thư viện Kafka
RUN pip install kafka-python hdfs

# Chuyển lại quyền về non-root nếu cần (hoặc giữ root nếu đơn giản)
# USER 1000 

# Copy code của bạn vào Image
COPY consumer.py /app/consumer.py