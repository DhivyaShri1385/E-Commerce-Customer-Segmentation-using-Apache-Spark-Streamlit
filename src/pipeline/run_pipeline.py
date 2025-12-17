
# src/pipeline/run_pipeline.py

import os
import sys
import argparse
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.functions import vector_to_array

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

class CustomerSegmentationPipeline:
    def __init__(self, input_path, output_path, k=4):
        self.input_path = input_path
        self.output_path = output_path
        self.k = k
        self.spark = self._create_spark_session()
        
    def _create_spark_session(self):
        # Create temp folder for logs
        base_tmp = os.path.join(os.getcwd(), "tmp", "spark-events")
        os.makedirs(base_tmp, exist_ok=True)
        
        return (
            SparkSession.builder
            .appName("CustomerAnalyticsPipeline")
            .config("spark.ui.enabled", "true")
            .config("spark.ui.port", "4040")
            .config("spark.eventLog.enabled", "false")
            .config("spark.hadoop.io.native.lib.available", "false")
            .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")
            .config("spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version", "1")
            .config("spark.hadoop.fs.permissions.umask-mode", "000")
            .config("spark.hadoop.mapreduce.fileoutputcommitter.marksuccessfuljobs", "false")
            .getOrCreate()
        )

    def load_data(self):
        print(f"Loading data from {self.input_path}...")
        self.df = self.spark.read.csv(self.input_path, header=True, inferSchema=True)
        # Basic validation
        if not self.df.head(1):
            raise ValueError("Input dataset is empty")
            
    def feature_engineering(self):
        print("Performing Feature Engineering (RFM)...")
        # RFM
        rfm = self.df.groupBy("CustomerID").agg(
            F.max("InvoiceDate").alias("LastPurchaseDate"),
            F.count("InvoiceNo").alias("Frequency"),
            F.sum("TotalPrice").alias("Monetary")
        )

        rfm = rfm.withColumn(
            "Recency",
            F.datediff(F.current_date(), F.col("LastPurchaseDate"))
        ).select("CustomerID", "Recency", "Frequency", "Monetary")

        # Additional Features
        numeric_features = [
            "Recency", "Frequency", "Monetary",
            "LoyaltyScore", "AvgBasketSize", "Returns",
            "SupportTickets", "ReferralCount", "AvgSessionTime"
        ]

        # Join back
        self.df_features = rfm.join(
            self.df.select("CustomerID", *numeric_features[3:]),
            on="CustomerID",
            how="left"
        ).drop_duplicates(["CustomerID"]) # Ensure no dupes from join

        # Scaling
        assembler = VectorAssembler(inputCols=numeric_features, outputCol="features")
        assembled = assembler.transform(self.df_features)
        
        scaler = StandardScaler(inputCol="features", outputCol="scaled_features", withMean=True, withStd=True)
        self.scaled_data = scaler.fit(assembled).transform(assembled)

    def perform_clustering(self):
        print(f"Clustering with K={self.k}...")
        kmeans = KMeans(k=self.k, seed=42, featuresCol="scaled_features", predictionCol="segment_id")
        self.kmeans_model = kmeans.fit(self.scaled_data)
        self.segmented = self.kmeans_model.transform(self.scaled_data)
        
        # Label Segments (Heuristic mapping, might need adjustment based on data)
        self.segmented = self.segmented.withColumn(
            "segment_name",
            F.when(F.col("segment_id") == 0, "Needs Attention")
             .when(F.col("segment_id") == 1, "Occasional Shoppers")
             .when(F.col("segment_id") == 2, "Champions")
             .otherwise("Loyalists")
        )

    def train_churn_model(self):
        print("Training Churn Prediction Model...")
        # Define Churn Label
        self.segmented = self.segmented.withColumn(
            "churn",
            F.when((F.col("Recency") > 180) & (F.col("Frequency") <= 2), 1).otherwise(0)
        )
        
        churn_features = ["Recency", "Frequency", "Monetary", "LoyaltyScore", "AvgBasketSize", "Returns"]
        churn_assembler = VectorAssembler(inputCols=churn_features, outputCol="churn_features")
        churn_data = churn_assembler.transform(self.segmented)
        
        train, test = churn_data.randomSplit([0.8, 0.2], seed=42)
        
        lr = LogisticRegression(featuresCol="churn_features", labelCol="churn", predictionCol="churn_prediction")
        self.churn_model = lr.fit(train)
        
        # Eval
        predictions = self.churn_model.transform(test)
        evaluator = BinaryClassificationEvaluator(labelCol="churn", metricName="areaUnderROC")
        auc = evaluator.evaluate(predictions)
        print(f"Churn Model AUC: {auc}")
        
        self.final_df = self.churn_model.transform(churn_data)

    def save_output(self):
        print(f"Saving output to {self.output_path}...")
        
        final_df_clean = (
            self.final_df
            .withColumn("churn_probability", vector_to_array("probability")[1])
            .drop("features", "scaled_features", "churn_features", "probability", "rawPrediction")
        )

        pandas_df = final_df_clean.toPandas()
        
        output_dir = os.path.join(self.output_path, "clustered_output")
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, "final_output.csv")
        pandas_df.to_csv(output_file, index=False)
        print(f"✅ Successfully saved to {output_file}")

    def run(self):
        self.load_data()
        self.feature_engineering()
        self.perform_clustering()
        self.train_churn_model()
        self.save_output()
        print("Pipeline Completed Successfully.")
        
    def stop(self):
        self.spark.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Customer Segmentation Spark Pipeline")
    parser.add_argument("--input", required=False, default="data/customer_data.csv", help="Path to input CSV")
    parser.add_argument("--output", required=False, default="output", help="Path to output directory")
    parser.add_argument("--k", type=int, default=4, help="Number of clusters")
    parser.add_argument("--keep-alive", action="store_true", help="Keep Spark session alive for UI monitoring")
    
    args = parser.parse_args()
    
    pipeline = CustomerSegmentationPipeline(args.input, args.output, args.k)
    try:
        pipeline.run()
        if args.keep_alive:
            print("\n" + "="*50)
            print("🚀 Spark Web UI is active at http://localhost:4040")
            print("Press Ctrl+C to stop the session...")
            print("="*50)
            import time
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping Spark session...")
    except Exception as e:
        print(f"Pipeline Failed: {e}")
    finally:
        pipeline.stop()
