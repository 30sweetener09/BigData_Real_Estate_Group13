from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, from_json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from pyspark.sql.types import (
    StructType, StructField,
    StringType, IntegerType, LongType,
    BooleanType, ArrayType, DoubleType
)
from pyspark.sql.functions import col, when
from pymongo.errors import DuplicateKeyError
import sys
print("pymongo ver")
def main():
    spark = SparkSession.builder \
        .appName("Kafka-Stream") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    
    kafka_broker = "kafka-0.kafka-service.kafka.svc.cluster.local:9092"
    topic_name = "data-stream"
    
    print("=" * 60)
    print("🚀 SPARK STREAMING BẮT ĐẦU")
    print(f"Kafka Broker: {kafka_broker}")
    print(f"Topic: {topic_name}")
    print("MongoDB: mydb.kafka_data (via pymongo) +authen + ver 2")
    print("=" * 60)
    
    try:
        kafka_df = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", kafka_broker) \
            .option("subscribe", topic_name) \
            .option("startingOffsets", "latest") \
            .option("failOnDataLoss", "false") \
            .load()
        
        print("✓ Đã kết nối Kafka stream")
        
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
        kafka_message_schema = StructType([
            StructField("id", LongType(), True),
            StructField("value", value_schema, True),
            StructField("timestamp", DoubleType(), True),  # time.time() -> float
            StructField("cycle", IntegerType(), True)
        ])
        
        parsed_df = kafka_df.select(
            from_json(
                col("value").cast("string"),
                kafka_message_schema
            ).alias("data"),
            col("timestamp").alias("kafka_timestamp"),
            col("partition"),
            col("offset")
        )
        flattened_df = parsed_df.select(
            "data.id",
            "data.timestamp",
            "data.cycle",
            "data.value.ad.*",
            "kafka_timestamp",
            "partition",
            "offset"
        ).withColumn("processed_at", current_timestamp())
        
        processed_df = (
            flattened_df
            .drop("id")                         # ⬅ xoá id cũ
            .withColumnRenamed("list_id", "id") # ⬅ chỉ còn 1 id

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
        
        print("✓ Đã cấu hình data processing")
        
        # Dùng pymongo thay vì mongo-spark-connector
        def write_to_mongodb_pymongo(batch_df, batch_id):
            from pymongo import MongoClient
            
            count = batch_df.count()
            print(f"\n{'='*60}")
            print(f"[Batch #{batch_id}] Nhận được {count} messages")
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
        
        query = processed_df.writeStream \
            .foreachBatch(write_to_mongodb_pymongo) \
            .outputMode("append") \
            .option("checkpointLocation", "/tmp/spark-checkpoint") \
            .trigger(processingTime="10 seconds") \
            .start()
        
        print("\n" + "=" * 60)
        print("💡 Spark Streaming đang chạy...")
        print("💡 Gửi message vào Kafka để test")
        print("💡 Nhấn Ctrl+C để dừng")
        print("=" * 60 + "\n")
        
        query.awaitTermination()
        
    except KeyboardInterrupt:
        print("\n\n===== Dừng Spark Streaming =====")
        spark.stop()
    except Exception as e:
        print(f"\n✗ Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()