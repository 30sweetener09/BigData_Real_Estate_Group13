from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum, avg, max, min
import sys

# ==================== CẤU HÌNH ====================
# HDFS NameNode URL
HDFS_NAMENODE = 'hdfs://my-hadoop-hadoop-hdfs-nn-0.my-hadoop-hadoop-hdfs-nn.default.svc.cluster.local:9000'

# Đường dẫn file JSON trong HDFS
HDFS_INPUT_PATH = '/data/stream/*.json'  # Đọc tất cả file JSON
# HDFS_INPUT_PATH = '/data/stream/data-2024-01-01.json'  # Đọc 1 file cụ thể

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
        # Đọc JSON với multiLine=True nếu mỗi file là 1 JSON object
        df = (
            spark.read
            .option("multiLine", "true")
            .option("mode", "PERMISSIVE")
            .json(input_path)
        )
                
        record_count = df.count()
        print(f"✓ Đọc thành công {record_count:,} bản ghi")
        
        # Hiển thị schema
        print("\n📋 Schema của dữ liệu:")
        df.printSchema()
        
        return df
        
    except Exception as e:
        print(f"❌ Lỗi khi đọc dữ liệu: {e}")
        sys.exit(1)

def process_data(df):
    print("\n⚙️ Đang xử lý dữ liệu...")

    print("\n📐 Schema:")
    df.printSchema()

    print("\n📊 Số dòng:")
    print(df.count())
    print("\n📊 1 dòng đầu tiên:")
    df.select("*").limit(1).show(truncate=False)
    
    
    
    return df

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