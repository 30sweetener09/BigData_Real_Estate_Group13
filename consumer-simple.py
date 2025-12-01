import json
import time
from kafka import KafkaConsumer
import sys
import subprocess
from datetime import datetime
import os

# ==================== CẤU HÌNH ====================
KAFKA_BROKER = 'kafka-0.kafka-service.kafka.svc.cluster.local:9092'
TOPIC_NAME = 'data-stream'
GROUP_ID = 'hdfs-consumer-group'
HDFS_OUTPUT_DIR = '/data/stream'
# ==================================================

def create_consumer():
    """Tạo Kafka consumer"""
    print(f"Đang kết nối tới Kafka broker: {KAFKA_BROKER}")
    max_retries = 10
    
    for attempt in range(1, max_retries + 1):
        try:
            consumer = KafkaConsumer(
                TOPIC_NAME,
                bootstrap_servers=KAFKA_BROKER,
                group_id=GROUP_ID,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                max_poll_records=10,
                request_timeout_ms=120000,
                session_timeout_ms=60000,
                heartbeat_interval_ms=20000
            )
            print(f"✓ Kết nối Kafka thành công!")
            return consumer
        except Exception as e:
            print(f"✗ Lần thử {attempt}/{max_retries}: {e}")
            if attempt < max_retries:
                time.sleep(5)
    sys.exit(1)

def ensure_hdfs_directory():
    """Tạo thư mục HDFS nếu chưa tồn tại"""
    print(f"\nKiểm tra thư mục HDFS: {HDFS_OUTPUT_DIR}")
    try:
        result = subprocess.run(
            ['hdfs', 'dfs', '-test', '-d', HDFS_OUTPUT_DIR],
            capture_output=True
        )
        if result.returncode != 0:
            subprocess.run(['hdfs', 'dfs', '-mkdir', '-p', HDFS_OUTPUT_DIR], check=True)
            print(f"✓ Đã tạo thư mục")
        else:
            print(f"✓ Thư mục đã tồn tại")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)

def write_to_hdfs(data, output_dir):
    """Ghi dữ liệu vào HDFS bằng hdfs dfs -put"""
    try:
        # Tạo file tạm
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        temp_file = f"/tmp/data_{timestamp}.json"
        hdfs_path = f"{output_dir}/data_{timestamp}.json"
        
        # Ghi file local
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Put vào HDFS
        result = subprocess.run(
            ['hdfs', 'dfs', '-put', temp_file, hdfs_path],
            capture_output=True,
            text=True
        )
        
        # Xóa file tạm
        os.remove(temp_file)
        
        if result.returncode == 0:
            return True, hdfs_path
        else:
            return False, result.stderr
            
    except Exception as e:
        return False, str(e)

def consume_and_store(consumer, output_dir):
    """Nhận message và lưu vào HDFS"""
    print(f"\n{'='*70}")
    print(f"BẮT ĐẦU NHẬN VÀ LƯU DỮ LIỆU")
    print(f"{'='*70}")
    print(f"Topic: {TOPIC_NAME}")
    print(f"HDFS: {output_dir}")
    print(f"{'='*70}\n")
    
    message_count = 0
    success_count = 0
    error_count = 0
    
    try:
        for message in consumer:
            try:
                data = message.value
                message_count += 1
                record_id = data.get('id', 'N/A')
                
                print(f"\n[{message_count:4d}] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"       ✓ Nhận: ID={record_id}")
                
                success, result = write_to_hdfs(data, output_dir)
                
                if success:
                    success_count += 1
                    filename = result.split('/')[-1]
                    print(f"       ✓ Lưu: {filename}")
                else:
                    error_count += 1
                    print(f"       ✗ Lỗi: {result}")
                
                print(f"       📊 {success_count} thành công, {error_count} lỗi")
                
            except KeyboardInterrupt:
                raise
            except Exception as e:
                error_count += 1
                print(f"\n[{message_count:4d}] ✗ Lỗi: {e}")
                
    except KeyboardInterrupt:
        print(f"\n\n{'='*70}")
        print("DỪNG CONSUMER")
        print(f"{'='*70}")
        print(f"Tổng: {message_count} | Thành công: {success_count} | Lỗi: {error_count}")
        consumer.close()
        print(f"{'='*70}\n")

def main():
    print("\n" + "="*70)
    print("KAFKA CONSUMER - HDFS WRITER (HDFS CLI)")
    print("="*70)
    print(f"Kafka: {KAFKA_BROKER}")
    print(f"Topic: {TOPIC_NAME}")
    print(f"HDFS:  {HDFS_OUTPUT_DIR}")
    print("="*70 + "\n")
    
    consumer = create_consumer()
    ensure_hdfs_directory()
    consume_and_store(consumer, HDFS_OUTPUT_DIR)

if __name__ == "__main__":
    main()