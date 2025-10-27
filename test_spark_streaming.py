import os
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, LongType, IntegerType, BooleanType
from pyspark.sql.functions import col, from_json, get_json_object

# Thiết lập (tùy chọn, có thể bỏ qua nếu không cần)
os.environ['HADOOP_HOME'] = r'C:\hadoop'

print("="*80)
print("REAL ESTATE DATA STREAMING PROCESSOR - SPARK 4.0.1")
print("="*80)

# Tạo SparkSession
spark = SparkSession.builder \
    .appName("RealEstateStreaming") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "2") \
    .config("spark.sql.streaming.schemaInference", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
print(f"✓ Spark {spark.version} started\n")

# Định nghĩa schema cho nested JSON
# Schema cho phần "ad" bên trong "data"
ad_schema = StructType([
    StructField("ad_id", LongType(), True),
    StructField("list_id", LongType(), True),
    StructField("list_time", LongType(), True),
    StructField("state", StringType(), True),
    StructField("type", StringType(), True),
    StructField("account_name", StringType(), True),
    StructField("phone", StringType(), True),
    StructField("region", IntegerType(), True),
    StructField("category", IntegerType(), True),
    StructField("company_ad", BooleanType(), True),
    StructField("subject", StringType(), True),
    StructField("body", StringType(), True)
])

# Schema cho phần "data"
data_schema = StructType([
    StructField("ad", ad_schema, True)
])

# Schema tổng thể
main_schema = StructType([
    StructField("id", StringType(), True),
    StructField("data", data_schema, True)
])

# Đường dẫn input
input_path = r"D:\20251\Lưu trữ và xử lý dữ liệu lớn\project\github\BigData_Real_Estate_Group13\streaming_input"
input_path = input_path.replace("\\", "/")

print(f"Input directory: {input_path}\n")
print("="*80)
print("STREAMING QUERY STARTING...")
print("="*80 + "\n")

try:
    # Đọc streaming data
    stream_df = spark.readStream \
        .schema(main_schema) \
        .option("maxFilesPerTrigger", 1) \
        .json(input_path)
    
    print("✓ Stream reader created")
    
    # Parse dữ liệu nested
    processed_df = stream_df.select(
        col("id").alias("list_id"),
        col("data.ad.ad_id"),
        col("data.ad.list_time"),
        col("data.ad.state"),
        col("data.ad.type"),
        col("data.ad.account_name"),
        col("data.ad.phone"),
        col("data.ad.region"),
        col("data.ad.category"),
        col("data.ad.company_ad"),
        col("data.ad.subject"),
        col("data.ad.body")
    )
    
    # Hiển thị schema
    print("\nProcessed Schema:")
    processed_df.printSchema()
    
    # Viết ra console
    query = processed_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .option("numRows", 5) \
        .trigger(processingTime='5 seconds') \
        .start()
    
    print("\n" + "="*80)
    print("✓ STREAMING QUERY STARTED SUCCESSFULLY!")
    print("="*80)
    print(f"\nMonitoring: {input_path}")
    print("Add new JSON files to see them processed in real-time")
    print("\nPress Ctrl+C to stop")
    print("="*80 + "\n")
    
    # Chờ query chạy
    query.awaitTermination()
    
except KeyboardInterrupt:
    print("\n\nStopping streaming query...")
    query.stop()
    print("✓ Query stopped successfully")
    
except Exception as e:
    print(f"\n{'='*80}")
    print("ERROR OCCURRED")
    print("="*80)
    print(f"Error: {str(e)}\n")
    import traceback
    traceback.print_exc()
    
finally:
    spark.stop()
    print("\n✓ SparkSession stopped")
    print("="*80)