from pyspark.sql import SparkSession
from pyspark.sql.functions import col, upper

# 1. Cấu hình Spark Session với Mongo Connector
spark = SparkSession.builder \
    .appName("HDFS_to_Mongo") \
    .config("spark.mongodb.write.connection.uri", "mongodb://my-mongodb.default.svc.cluster.local:27017/bigdata_db.users") \
    .getOrCreate()

# 2. Đọc dữ liệu từ HDFS
# Lưu ý: Port mặc định IPC của Hadoop thường là 9000 hoặc 8020. 
# Dựa trên tên pod của bạn, ta dùng service DNS đầy đủ.
hdfs_path = "hdfs://my-hadoop-hadoop-hdfs-nn-0.default.svc.cluster.local:9000/test.json"

print("--- Dang doc du lieu tu HDFS ---")
df = spark.read.csv(hdfs_path, header=True, inferSchema=True)
df.show()

# 3. Xử lý đơn giản (Ví dụ: Chuyển tên thành in hoa)
print("--- Dang xu li du lieu ---")
df_processed = df.withColumn("name_upper", upper(col("name")))
df_processed.show()

# 4. Lưu vào MongoDB
print("--- Dang luu vao MongoDB ---")
df_processed.write \
    .format("mongodb") \
    .mode("append") \
    .save()

print("--- Hoan thanh! ---")
spark.stop()