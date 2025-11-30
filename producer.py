# producer.py
from kafka import KafkaProducer
import time
import json
import logging
# Khi chạy cùng namespace, chỉ cần tên Service ngắn gọn
KAFKA_BROKER = 'kafka-service:9092' 
TOPIC = 'raw_data'
DATA_FILE = 'all_raw_data.json'
"""
import logging
# Bật chế độ Debug để nếu lỗi thì nó hiện chi tiết tại sao
logging.basicConfig(level=logging.DEBUG)
"""
def run_producer():
    print(f"Đang kết nối tới Kafka tại {KAFKA_BROKER}...")
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    print(f"Đang đọc toàn bộ file {DATA_FILE}...")
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            # Đọc TOÀN BỘ file vào một dictionary lớn
            full_data_dict = json.load(f) 
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file dữ liệu {DATA_FILE}.")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Lỗi: File JSON không hợp lệ. Vui lòng kiểm tra file JSON phải là một đối tượng Dictionary hợp lệ. Lỗi: {e}")
        return

    print(f"Bắt đầu gửi {len(full_data_dict)} bản ghi...")
    
    # Lặp qua từng cặp Key (ID) và Value (Bản ghi chi tiết)
    for record_id, record_value in full_data_dict.items():
        
        # Gửi toàn bộ value (là bản ghi chi tiết)
        # record_value là: {"ad": {...}}
        producer.send(TOPIC, value=record_value)
        print(f"✅ Gửi thành công ID: {record_id}")
        
        time.sleep(10) # Giả lập độ trễ 2 giây
            
    producer.flush()
    print("Hoàn tất gửi dữ liệu.")

if __name__ == '__main__':
    run_producer()