import json
import time
from kafka import KafkaProducer
import sys

# ==================== CẤU HÌNH ====================
KAFKA_BROKER = 'kafka-0.kafka-service.kafka.svc.cluster.local:9092'
TOPIC_NAME = 'data-stream'
DATA_FILE = '/data.json'  # File data trong pod
INTERVAL = 10  # Gửi dữ liệu mỗi 10 giây
# ==================================================

def create_producer():
    """Tạo Kafka producer với retry logic"""
    print(f"Đang kết nối tới Kafka broker: {KAFKA_BROKER}")
    max_retries = 10
    
    for attempt in range(1, max_retries + 1):
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8'),
                acks='all',
                retries=5,
                max_block_ms=120000,  # Tăng timeout lên 120 giây
                request_timeout_ms=120000,
                metadata_max_age_ms=300000,
                api_version_auto_timeout_ms=20000
            )
            print(f"✓ Kết nối Kafka thành công!")
            # Test gửi message đơn giản
            print("✓ Đang test kết nối...")
            future = producer.send(TOPIC_NAME, key='test', value={'test': 'connection'})
            future.get(timeout=30)
            print(f"✓ Test thành công! Producer sẵn sàng.")
            return producer
        except Exception as e:
            print(f"✗ Lần thử {attempt}/{max_retries} thất bại: {e}")
            if attempt < max_retries:
                print(f"  Đợi 5 giây trước khi thử lại...")
                time.sleep(5)
    
    print("❌ Không thể kết nối tới Kafka sau nhiều lần thử")
    sys.exit(1)

def load_data(file_path):
    """Đọc dữ liệu từ file JSON"""
    print(f"\nĐang đọc dữ liệu từ: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, dict):
            print(f"❌ File JSON phải có dạng dict/object, không phải {type(data)}")
            sys.exit(1)
            
        print(f"✓ Đã đọc {len(data)} records từ file")
        print(f"  Keys: {list(data.keys())[:5]}{'...' if len(data) > 5 else ''}")
        return data
        
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file: {file_path}")
        print(f"  Hãy copy file data vào pod bằng lệnh:")
        print(f"  minikube kubectl -- cp your_data.json kafka/my-producer:/data.json")
        sys.exit(1)
        
    except json.JSONDecodeError as e:
        print(f"❌ Lỗi đọc JSON: {e}")
        print(f"  File phải có format JSON hợp lệ")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
        sys.exit(1)

def send_data(producer, data, topic):
    """Gửi dữ liệu lên Kafka theo chu kỳ"""
    print(f"\n{'='*70}")
    print(f"BẮT ĐẦU GỬI DỮ LIỆU")
    print(f"{'='*70}")
    print(f"Topic: {topic}")
    print(f"Interval: {INTERVAL} giây")
    print(f"Tổng số records: {len(data)}")
    print(f"{'='*70}\n")
    
    record_count = 0
    cycle_count = 0
    
    try:
        while True:
            cycle_count += 1
            print(f"\n--- Chu kỳ #{cycle_count} ---")
            
            for record_id, value in data.items():
                try:
                    # Tạo message
                    message = {
                        'id': record_id,
                        'value': value,
                        'timestamp': time.time(),
                        'cycle': cycle_count
                    }
                    
                    # Gửi message
                    future = producer.send(topic, key=record_id, value=message)
                    result = future.get(timeout=10)
                    
                    record_count += 1
                    
                    # In thông tin
                    print(f"[{record_count:4d}] ✓ ID: {record_id:20s}")
                    
                    # Đợi trước khi gửi message tiếp theo
                    time.sleep(INTERVAL)
                    
                except KeyboardInterrupt:
                    raise
                    
                except Exception as e:
                    print(f"[{record_count:4d}] ✗ Lỗi gửi: {e}")
                    time.sleep(5)
                    
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("DỪNG PRODUCER")
        print("="*70)
        print(f"Tổng số messages đã gửi: {record_count}")
        print(f"Số chu kỳ hoàn thành: {cycle_count}")
        producer.flush()
        producer.close()
        print("✓ Đã đóng kết nối Kafka")
        print("="*70 + "\n")

def main():
    """Main function"""
    print("\n" + "="*70)
    print("KAFKA PRODUCER - DATA STREAM SIMULATOR")
    print("="*70)
    print(f"Kafka Broker   : {KAFKA_BROKER}")
    print(f"Topic          : {TOPIC_NAME}")
    print(f"Data File      : {DATA_FILE}")
    print(f"Send Interval  : {INTERVAL} giây")
    print("="*70 + "\n")
    
    # Tạo producer
    producer = create_producer()
    
    # Đọc dữ liệu
    data = load_data(DATA_FILE)
    
    # Gửi dữ liệu
    send_data(producer, data, TOPIC_NAME)

if __name__ == "__main__":
    main()