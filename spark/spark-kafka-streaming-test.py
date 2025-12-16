from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, from_json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
import sys
print("pymongo ver")
def main():
    spark = SparkSession.builder \
        .appName("Kafka-Stream") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    
    kafka_broker = "kafka-0.kafka-service.kafka.svc.cluster.local:9092"
    topic_name = "test"
    
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
        
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("value", DoubleType(), True),
            StructField("timestamp", StringType(), True),
            StructField("category", StringType(), True)
        ])
        
        parsed_df = kafka_df.select(
            col("key").cast("string"),
            from_json(col("value").cast("string"), schema).alias("data"),
            col("timestamp").alias("kafka_timestamp"),
            col("partition"),
            col("offset")
        )
        
        flattened_df = parsed_df.select(
            "key",
            "data.*",
            "kafka_timestamp",
            "partition",
            "offset"
        ).withColumn("processed_at", current_timestamp())
        
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
                    "mongodb://my-mongodb:27017/",
                    username="root",  # Hoặc admin
                    password="WJpHwyJqi5",  # THAY PASSWORD
                    authSource="admin"
                )
                
                # Hoặc dùng connection string đầy đủ
                # client = MongoClient("mongodb://username:password@my-mongodb:27017/?authSource=admin")
                
                db = client["mydb"]
                collection = db["kafka_data"]
                
                records = []
                for row in batch_df.collect():
                    record = row.asDict()
                    for key, value in record.items():
                        if hasattr(value, 'isoformat'):
                            record[key] = value.isoformat()
                    records.append(record)
                
                if records:
                    result = collection.insert_many(records)
                    print(f"✅ Đã lưu {len(result.inserted_ids)} records vào MongoDB")
                
                client.close()
            else:
                print("⏳ Không có message mới, đang đợi...")
        
        query = flattened_df.writeStream \
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