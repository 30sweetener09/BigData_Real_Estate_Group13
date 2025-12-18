import json
import time
from kafka import KafkaConsumer
from hdfs import InsecureClient
import sys
from datetime import datetime

# ==================== CẤU HÌNH ====================
# Thử các tên service Kafka sau (uncomment cái nào đúng):
KAFKA_BROKER = 'kafka-0.kafka-service.kafka.svc.cluster.local:9092'


TOPIC_NAME = 'data-stream'
GROUP_ID = 'hdfs-consumer-group'

# HDFS URL - thử các cách sau:
HDFS_URL = 'http://my-hadoop-hadoop-hdfs-nn-0.my-hadoop-hadoop-hdfs-nn.default.svc.cluster.local:9870'
# HDFS_URL = 'http://my-hadoop-hadoop-hdfs-nn-0:9870'  # Nếu cùng namespace
# HDFS_URL = 'http://localhost:9870'  # Nếu dùng port-forward

HDFS_USER = 'root'  # Đổi từ 'hdfs' sang 'root'
HDFS_OUTPUT_DIR = '/data/stream'
# ==================================================

def create_consumer():
    """Tạo Kafka consumer với retry logic"""
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
                request_timeout_ms=120000,  # Tăng timeout lên
                session_timeout_ms=60000,
                heartbeat_interval_ms=20000,
                api_version_auto_timeout_ms=20000
            )
            print(f"✓ Kết nối Kafka thành công!")
            print(f"✓ Subscribed topic: {TOPIC_NAME}")
            print(f"✓ Consumer group: {GROUP_ID}")
            return consumer
        except Exception as e:
            print(f"✗ Lần thử {attempt}/{max_retries} thất bại: {e}")
            if attempt < max_retries:
                print(f"  Đợi 5 giây trước khi thử lại...")
                time.sleep(5)
    
    print("❌ Không thể kết nối tới Kafka sau nhiều lần thử")
    sys.exit(1)

def create_hdfs_client():
    """Tạo HDFS client với retry logic"""
    print(f"\nĐang kết nối tới HDFS: {HDFS_URL}")
    max_retries = 10
    
    for attempt in range(1, max_retries + 1):
        try:
            client = InsecureClient(HDFS_URL, user=HDFS_USER)
            # Test connection
            client.status('/')
            print(f"✓ Kết nối HDFS thành công!")
            print(f"✓ User: {HDFS_USER}")
            return client
        except Exception as e:
            print(f"✗ Lần thử {attempt}/{max_retries} thất bại: {e}")
            if attempt < max_retries:
                print(f"  Đợi 5 giây trước khi thử lại...")
                time.sleep(5)
    
    print("❌ Không thể kết nối tới HDFS sau nhiều lần thử!")
    print("  Kiểm tra HDFS có đang chạy không:")
    print("  minikube kubectl -- get pods | findstr hdfs")
    sys.exit(1)

def ensure_hdfs_directory(client, directory):
    """Đảm bảo thư mục HDFS tồn tại"""
    print(f"\nKiểm tra thư mục output: {directory}")
    try:
        client.status(directory)
        print(f"✓ Thư mục đã tồn tại!")
    except:
        try:
            client.makedirs(directory)
            print(f"✓ Đã tạo thư mục mới!")
        except Exception as e:
            print(f"❌ Lỗi tạo thư mục: {e}")
            sys.exit(1)

def write_to_hdfs(client, data, output_dir):
    """Ghi dữ liệu vào HDFS"""
    try:
        # Tạo tên file với timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"data_{timestamp}.json"
        filepath = f"{output_dir}/{filename}"
        
        # Ghi file
        with client.write(filepath, encoding='utf-8', overwrite=True) as writer:
            json.dump(data, writer, ensure_ascii=False, indent=2)
        
        return True, filepath
        
    except Exception as e:
        return False, str(e)

def consume_and_store(consumer, hdfs_client, output_dir):
    """Nhận message từ Kafka và lưu vào HDFS"""
    print(f"\n{'='*70}")
    print(f"BẮT ĐẦU NHẬN VÀ LƯU DỮ LIỆU")
    print(f"{'='*70}")
    print(f"Đang lắng nghe topic: {TOPIC_NAME}")
    print(f"Lưu vào HDFS: {output_dir}")
    print(f"{'='*70}\n")
    
    message_count = 0
    success_count = 0
    error_count = 0
    
    try:
        for message in consumer:
            try:
                data = message.value
                message_count += 1
                
                # Hiển thị thông tin message
                record_id = data.get('id', 'N/A')
                record_value = data.get('value', 'N/A')
                
                print(f"\n[{message_count:4d}] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"       ✓ Nhận: ID={record_id}")
                
                # Ghi vào HDFS
                success, result = write_to_hdfs(hdfs_client, data, output_dir)
                
                if success:
                    success_count += 1
                    filename = result.split('/')[-1]
                    print(f"       ✓ Lưu: {filename}")
                    print(f"       📊 Thống kê: {success_count} thành công, {error_count} lỗi")
                else:
                    error_count += 1
                    print(f"       ✗ Lỗi: {result}")
                    print(f"       📊 Thống kê: {success_count} thành công, {error_count} lỗi")
                
            except KeyboardInterrupt:
                raise
                
            except Exception as e:
                error_count += 1
                print(f"\n[{message_count:4d}] ✗ Lỗi xử lý message: {e}")
                continue
                
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("DỪNG CONSUMER")
        print("="*70)
        print(f"Tổng messages nhận: {message_count}")
        print(f"Lưu thành công    : {success_count}")
        print(f"Lỗi               : {error_count}")
        consumer.close()
        print("✓ Đã đóng kết nối Kafka")
        print("="*70 + "\n")

def main():
    """Main function"""
    print("\n" + "="*70)
    print("KAFKA CONSUMER - HDFS WRITER")
    print("="*70)
    print(f"Kafka Broker   : {KAFKA_BROKER}")
    print(f"Topic          : {TOPIC_NAME}")
    print(f"Consumer Group : {GROUP_ID}")
    print(f"HDFS URL       : {HDFS_URL}")
    print(f"Output Dir     : {HDFS_OUTPUT_DIR}")
    print("="*70 + "\n")
    
    # Tạo consumer
    consumer = create_consumer()
    
    # Tạo HDFS client
    hdfs_client = create_hdfs_client()
    
    # Đảm bảo thư mục output tồn tại
    ensure_hdfs_directory(hdfs_client, HDFS_OUTPUT_DIR)
    
    # Bắt đầu consume và lưu
    consume_and_store(consumer, hdfs_client, HDFS_OUTPUT_DIR)

if __name__ == "__main__":
    main()