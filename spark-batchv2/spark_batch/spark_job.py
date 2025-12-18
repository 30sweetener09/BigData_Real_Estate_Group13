from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
# from schema import BATCHING_SPARK_BATCH_CONFIG_SCHEMA 

MONGO_URI = "mongodb://127.0.0.1:27017/real_estate.properties"
DATA_LINK = "hdfs://localhost:9000/data/nhatot/data_lines.json"
HDFS_URI = "hdfs://localhost:9000"
MONGO_SPARK_CONNECTOR = "org.mongodb.spark:mongo-spark-connector_2.12:3.0.2"

def main():
    spark = SparkSession.builder \
        .appName("RealEstateBatchJob") \
        .config("spark.hadoop.fs.defaultFS", HDFS_URI) \
        .config("spark.mongodb.write.connection.uri", MONGO_URI) \
        .config("spark.jars.packages", MONGO_SPARK_CONNECTOR) \
        .getOrCreate()

    print("🚀 Spark started")

    df = spark.read.json(DATA_LINK)

    final_df = df.select(
        col("id").cast("string"),
        col("data.ad.price").cast("double").alias("price"),
        col("data.ad.width").cast("double").alias("width"),            
        col("data.ad.length").cast("double").alias("length"),      
        col("data.ad.street_name").alias("street_name"),
        col("data.ad.category_name").alias("category_name"),
        col("data.ad.rooms").cast("int").alias("rooms"),              
        col("data.ad.size").cast("double").alias("size"),   
        col("data.ad.living_size").cast("double").alias("living_size"),
        col("data.ad.ward_name").alias("ward"),      
        col("data.ad.area_name").alias("area"),      
        col("data.ad.region_name").alias("region"),  
        col("data.ad.is_main_street").cast("boolean").alias("is_main_street"),
        # Xử lý logic property_legal_document: nếu > 0 là có sổ (True)
        when(col("data.ad.property_legal_document") > 0, True).otherwise(False).alias("property_legal_document"),
        # Xử lý logic status: nếu property_status == 1 (hoặc tùy logic) là đang bán
        when(col("data.ad.property_status") == 1, True).otherwise(False).alias("status")
    )

    print("======== TRANSFORMED DATA =========")
    final_df.show(5)
    final_df.printSchema()

    final_df.write \
        .format("mongo") \
        .mode("overwrite") \
        .option("uri", MONGO_URI) \
        .save()

    print("✅ Write to MongoDB completed!")
    spark.stop()

if __name__ == "__main__":
    main()