import json
import os
import sys
from pymongo import MongoClient

# CẤU HÌNH KẾT NỐI
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "real_estate_db"
COLLECTION_NAME = "listings"

def get_db_connection():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Kiểm tra kết nối thử
        client.server_info()
        return client[DB_NAME][COLLECTION_NAME]
    except Exception as e:
        print(f"❌ LỖI KẾT NỐI: Không tìm thấy MongoDB tại {MONGO_URI}")
        sys.exit(1)

def clean_data():
    col = get_db_connection()
    col.delete_many({})
    print("Đã xóa dữ liệu giả lập trong DB. Sẵn sàng Spark!")

def import_data():
    col = get_db_connection()
    # Tìm file JSON
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    file_path = os.path.join(project_root, "producer_kafka", "all_raw_data.json")

    print(f"📂 Đang đọc dữ liệu thô từ: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        data_list = list(raw_data.values()) if isinstance(raw_data, dict) else raw_data

        print(f"✅ Tìm thấy {len(data_list)} bản ghi thô. Bắt đầu lọc và chuẩn hóa...")
        # Mapping dữ liệu chuẩn
        clean_docs = []
        for item in data_list:
            ad = item.get('ad', {})
            if not ad: continue

            try:
                # Chuẩn hóa
                def get_int(val):
                    try: return int(str(val).replace('.', '').replace(',', '')) if val else 0
                    except: return 0
            
                def get_float(val):
                    try: return float(str(val).replace(',', '.')) if val else 0.0
                    except: return 0.0

                def get_bool(val):
                    return bool(val)

                doc = {
                    "id": str(ad.get("list_id", "")), 
                    "price": get_int(ad.get("price")),
                    "width": get_float(ad.get("width")),
                    "length": get_float(ad.get("length")),
                    "street_name": str(ad.get("street_name", "")),
                    "category_name": str(ad.get("category_name", "")),
                    "rooms": get_int(ad.get("rooms")),
                    "size": get_float(ad.get("size") or ad.get("area")), # Diện tích đất
                    "living_size": get_float(ad.get("living_size") or ad.get("size")), 
                    "ward": str(ad.get("ward_name", "")),
                    "area": str(ad.get("area_name", "")),
                    "region": str(ad.get("region_name", "")),
                    "list_time": ad.get("list_time"),
                    "latitude": get_float(ad.get("latitude")),   # Vĩ độ
                    "longitude": get_float(ad.get("longitude")), # Kinh độ
                    "is_main_street": get_bool(ad.get("is_main_street")), # Mặt đường
                    "property_legal_document": get_bool(ad.get("property_legal_document", 1)), # Có sổ đỏ?
                    "status": True # Mặc định là đang bán
                }
                if doc["price"] > 0:
                    clean_docs.append(doc)
            except: continue

        # Xóa dữ liệu cũ
        col.delete_many({})
        col.insert_many(clean_docs)
        print(f"THÀNH CÔNG! Đã nạp {len(clean_docs)} bản ghi vào Minikube MongoDB.")

    except FileNotFoundError:
        print("❌ Lỗi: Không tìm thấy file JSON. Kiểm tra lại đường dẫn.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        clean_data()
    else:
        import_data()