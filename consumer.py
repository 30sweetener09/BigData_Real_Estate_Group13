# consumer.py (Phiên bản Batching - Chống lỗi Lease)
import json
import logging
import time
from kafka import KafkaConsumer
from hdfs import InsecureClient

logging.basicConfig(level=logging.INFO)

# --- CẤU HÌNH ---
KAFKA_BROKER = 'localhost:9092'  # Đã hack hosts
TOPIC = 'raw_data'
# THAY IP HDFS MỚI CỦA BẠN VÀO ĐÂY
HDFS_HOST = 'http://10.244.0.50:9870' 
HDFS_USER = 'root'
HDFS_PATH = '/user/root/datalake/raw_data.json'
BATCH_SIZE = 10  # Gom 20 tin nhắn mới ghi 1 lần

def run_consumer():
    print("--- BẮT ĐẦU CONSUMER (BATCH MODE) ---")
    
    # 1. Kết nối HDFS
    try:
        client = InsecureClient(HDFS_HOST, user=HDFS_USER, timeout=30) # Tăng timeout
        print(f"-> Đã kết nối HDFS tại {HDFS_HOST}")
    except Exception as e:
        print(f"❌ Lỗi cấu hình HDFS: {e}")
        return

    # 2. Kết nối Kafka
    print(f"-> Đang kết nối Kafka...")
    try:
        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='my-batch-group', # Đổi group ID để đọc lại từ đầu cho chắc
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        print("-> Đã kết nối Kafka! Đang chờ tin nhắn...")
    except Exception as e:
        print(f"❌ Lỗi kết nối Kafka: {e}")
        return

    # 3. Vòng lặp xử lý Batch
    buffer = []
    
    for message in consumer:
        data = message.value
        
        # Lấy ID để in ra màn hình cho đẹp
        rec_id = "Unknown"
        if 'ad' in data and 'list_id' in data['ad']:
            rec_id = data['ad']['list_id']
        elif 'list_id' in data:
            rec_id = data['list_id']
            
        # Thêm vào bộ nhớ đệm
        buffer.append(json.dumps(data))
        print(f"📥 Đã nhận ID: {rec_id} (Buffer: {len(buffer)}/{BATCH_SIZE})")
        
        # Khi bộ nhớ đệm đầy, thực hiện ghi vào HDFS
        if len(buffer) >= BATCH_SIZE:
            print(f"⚡ Đang ghi {len(buffer)} bản ghi vào HDFS...")
            try:
                # Nối các dòng lại thành một chuỗi lớn
                content_block = "\n".join(buffer) + "\n"
                
                # Mở file và ghi 1 lần duy nhất
                with client.write(HDFS_PATH, encoding='utf-8', append=True) as writer:
                    writer.write(content_block)
                
                print("✅ Ghi Batch thành công!")
                buffer = [] # Xóa bộ nhớ đệm sau khi ghi xong
                time.sleep(1) # Nghỉ 1 chút để HDFS kịp nhả Lease (quan trọng)
                
            except Exception as e:
                print(f"❌ Lỗi ghi HDFS: {e}")
                # Nếu lỗi, giữ nguyên buffer để thử lại ở vòng sau (hoặc xử lý tùy ý)
                time.sleep(5) # Chờ 5s nếu lỗi Lease

if __name__ == '__main__':
    run_consumer()