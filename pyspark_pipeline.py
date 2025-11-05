import os
import sys
import findspark


findspark.init()

os.environ["HADOOP_HOME"] = "C:\\hadoop"
os.environ["PATH"] += os.pathsep + os.path.join(os.environ["HADOOP_HOME"], "bin")
os.environ["SPARK_LOCAL_DIRS"] = "C:\\tmp\\spark"
os.environ["PYSPARK_PYTHON"] = "python"

from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.sql import functions as F

def run_pipeline(input_csv, output_folder, k):
    print("\n Starting Spark Session...")
    spark = SparkSession.builder \
        .appName("ECommerce_Segmentation_Pipeline") \
        .config("spark.hadoop.fs.permission.umask-mode", "000") \
        .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.RawLocalFileSystem") \
        .config("spark.hadoop.fs.AbstractFileSystem.file.impl", "org.apache.hadoop.fs.local.LocalFs") \
        .config("spark.hadoop.fs.file.impl.disable.cache", "true") \
        .getOrCreate()

    print(f"\n Spark Web UI: {spark.sparkContext.uiWebUrl}")
    print(f"\n Reading input file: {input_csv}")

 
    data = spark.read.option("header", "true").option("inferSchema", "true").csv(input_csv)
    print("\n Data successfully loaded! Schema:")
    data.printSchema()

    assembler = VectorAssembler(inputCols=["Recency", "Frequency", "Monetary"], outputCol="features")
    assembled = assembler.transform(data)

    scaler = StandardScaler(inputCol="features", outputCol="scaledFeatures")
    scaled_data = scaler.fit(assembled).transform(assembled)

    print(f"\n Running KMeans with k = {k} ...")
    kmeans = KMeans(featuresCol="scaledFeatures", k=int(k), seed=1)
    model = kmeans.fit(scaled_data)
    clustered = model.transform(scaled_data)

    print("\n Clustering complete! Centers:")
    for center in model.clusterCenters():
        print(center)

    print("\n Sample clustered output:")
    clustered.select("CustomerID", "Recency", "Frequency", "Monetary", "prediction").show(10)

    
    print(f"\n Saving to local folder: {output_folder}\\clustered_output.csv")

    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "clustered_output.csv")

    
    pdf = clustered.select("CustomerID", "Recency", "Frequency", "Monetary", "prediction").toPandas()
    pdf.to_csv(output_path, index=False)

    print(f"\n Output saved successfully at: {output_path}")
    spark.stop()


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: spark-submit pyspark_pipeline.py <input_csv> <output_folder> <k>")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_folder = sys.argv[2]
    k = sys.argv[3]

    run_pipeline(input_csv, output_folder, k)
