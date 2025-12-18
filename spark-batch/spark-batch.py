from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, from_json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from pyspark.sql.types import (
    StructType, StructField,
    StringType, IntegerType, LongType,
    BooleanType, ArrayType, DoubleType
)
from pyspark.sql.functions import col, when
import sys
from pymongo.errors import DuplicateKeyError
# ==================== CẤU HÌNH ====================
# HDFS NameNode URL
HDFS_NAMENODE = 'hdfs://my-hadoop-hadoop-hdfs-nn-0.my-hadoop-hadoop-hdfs-nn.default.svc.cluster.local:9000'

# Đường dẫn file JSON trong HDFS
HDFS_INPUT_PATH = '/data/stream/*.json'  # Đọc tất cả file JSON
#HDFS_INPUT_PATH = '/data/stream/data_20251217_182714_458418.json'  # Đọc 1 file cụ thể

# Đường dẫn output (optional)
HDFS_OUTPUT_PATH = '/data/processed/output'

# App name
APP_NAME = 'HDFS-JSON-Processing'
# ==================================================

def create_spark_session():
    """Tạo Spark Session cho K8s"""
    print("\n🚀 Đang khởi tạo Spark Session...")
    
    spark = SparkSession.builder \
        .appName(APP_NAME) \
        .config("spark.hadoop.fs.defaultFS", HDFS_NAMENODE) \
        .config("spark.hadoop.dfs.client.use.datanode.hostname", "true") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    print("✓ Spark Session đã được khởi tạo!")
    print(f"✓ Spark Version: {spark.version}")
    print(f"✓ Master: {spark.sparkContext.master}")
    
    return spark

def read_json_from_hdfs(spark, input_path):
    """Đọc file JSON từ HDFS"""
    print(f"\n📖 Đang đọc dữ liệu từ: {input_path}")
    
    try:
        ad_schema = StructType([
            
            StructField("list_id", LongType(), True), #id
            StructField("price", LongType(), True), # giá
            StructField("rooms", IntegerType(), True), # số phòng ngủ
            StructField("size", DoubleType(), True), # diện tích 
            StructField("category_name", StringType(), True), #loại
            
            StructField("living_size", DoubleType(), True), # diện tích ở
            StructField("street_name", StringType(), True), # tên đường
            StructField("ward_name", StringType(), True), # Tên phường
            StructField("area_name", StringType(), True), # Quận 
            StructField("is_main_street", BooleanType(), True), # Đường chính?
            StructField("property_legal_document", IntegerType(), True), # sổ đỏ?
            StructField("status", StringType(), True) # Trạng thái
        ])
        value_schema = StructType([
            StructField("ad", ad_schema, True)
        ])
        json_schema = StructType([
            StructField("id", LongType(), True),
            StructField("value", value_schema, True),
            StructField("timestamp", DoubleType(), True),  # time.time() -> float
            StructField("cycle", IntegerType(), True)
        ])        
        # Đọc JSON với multiLine=True nếu mỗi file là 1 JSON object
        df = (
            spark.read
            .schema(json_schema)
            .option("multiLine", "true")
            .option("mode", "PERMISSIVE")
            .json(input_path)
        )
        
        
        
        return df
        
    except Exception as e:
        print(f"❌ Lỗi khi đọc dữ liệu: {e}")
        sys.exit(1)

def process_data(df):
    flattened_df = df.select(
        col("id"),
        col("timestamp").alias("kafka_timestamp"),
        col("cycle"),
        col("value.ad.*")
    ).withColumn("processed_at", current_timestamp())
    #parsed_df.select("*").limit(2).show(truncate=False)
    #flattened_df.printSchema()
    #flattened_df.select("*").limit(2).show(truncate=False)
    processed_df = (
        flattened_df
        .drop("id")                         # ⬅ xoá id cũ
        .withColumnRenamed("list_id", "id")

        .withColumn(
            "property_legal_document",
            when(col("property_legal_document") == 1, True).otherwise(False)
        )
        .withColumn(
            "status",
            when(col("status") == "active", True).otherwise(False)
        )
        .filter(col("id").isNotNull())
    )
    #processed_df.printSchema()
    #processed_df.select("*").limit(2).show(truncate=False)
    print("✓ Đã cấu hình data processing")

    record_count = processed_df.count()
    print(f"✓ Đọc thành công {record_count:,} bản ghi")
    
    # Hiển thị schema
    print("\n📋 Schema của dữ liệu:")
    processed_df.printSchema()
    processed_df.select("*").limit(2).show(truncate=False)
    return processed_df
# Dùng pymongo thay vì mongo-spark-connector
def write_to_mongodb_pymongo(batch_df):
    from pymongo import MongoClient
    
    count = batch_df.count()
    print(f"\n{'='*60}")
    print(f"[Batch Nhận được {count} messages")
    print('='*60)
    
    if count > 0:
        batch_df.show(5, truncate=False)
        
        # MongoDB connection với auth
        # THAY username và password của bạn
        client = MongoClient(
            "mongodb://my-mongodb.default.svc.cluster.local:27017",
            username="root",  # Hoặc admin
            password="WJpHwyJqi5",  # THAY PASSWORD
            authSource="admin"
        )
        
        # Hoặc dùng connection string đầy đủ
        # client = MongoClient("mongodb://username:password@my-mongodb:27017/?authSource=admin")
        
        db = client["real_estate_db"]
        collection = db["listings"]

        collection.create_index("id", unique=True)

        records = []
        for row in batch_df.collect():
            record = row.asDict()
            for key, value in record.items():
                if hasattr(value, 'isoformat'):
                    record[key] = value.isoformat()
            records.append(record)
        
        if records:
            # Insert và bỏ qua records trùng id
            inserted_count = 0
            for record in records:
                try:
                    collection.insert_one(record)
                    inserted_count += 1
                except DuplicateKeyError:
                    print(f"⚠️ Bỏ qua record trùng id: {record.get('id')}")
            
            print(f"✅ Đã lưu {inserted_count}/{len(records)} records vào MongoDB")
        
        client.close()
    else:
        print("⏳ Không có message mới, đang đợi...")
def main():
    """Hàm chính"""
    print("=" * 60)
    print("  SPARK - HDFS JSON PROCESSING ON KUBERNETES")
    print("=" * 60)
    
    # 1. Tạo Spark Session
    spark = create_spark_session()
    
    

    try:
        # 2. Đọc dữ liệu từ HDFS
        df = read_json_from_hdfs(spark, HDFS_INPUT_PATH)
        
        # 3. Xử lý dữ liệu cơ bản
        df_processed = process_data(df)
        
        # 5. Lưu kết quả (optional)
        # save_to_hdfs(df_processed, HDFS_OUTPUT_PATH, format='parquet')
        
        print("\n" + "=" * 60)
        print("✅ XỬ LÝ HOÀN TẤT!")
        print("=" * 60)
        write_to_mongodb_pymongo(df_processed)

        
        print("\n" + "=" * 60)
        print("✅ Đã đẩy lên mongoDB")
        print("=" * 60)
        
        
    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình xử lý: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        # Đóng Spark Session
        spark.stop()
        print("\n👋 Spark Session đã đóng")

if __name__ == "__main__":
    main()