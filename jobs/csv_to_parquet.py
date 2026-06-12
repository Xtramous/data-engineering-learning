#!/usr/bin/env python3
"""
Day 3: First Spark Job
CSV to Parquet transformation for Bronze layer

This job demonstrates:
- Reading CSV files with Spark
- Basic schema definition
- Writing Parquet files with partitioning
- Basic error handling
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
import sys

def main():
    # Initialize Spark Session
    spark = SparkSession.builder \
        .appName("csv_to_parquet") \
        .master("local[4]") \
        .getOrCreate()

    # Set log level
    spark.sparkContext.setLogLevel("INFO")

    try:
        # Define schema for events
        schema = StructType([
            StructField("event_id", IntegerType(), True),
            StructField("user_id", StringType(), True),
            StructField("event_type", StringType(), True),
            StructField("timestamp", TimestampType(), True),
            StructField("value", IntegerType(), True)
        ])

        # Read CSV file
        print("📖 Reading CSV file...")
        df = spark.read \
            .schema(schema) \
            .option("header", "true") \
            .csv("/data/sample_events.csv")

        # Basic validation
        row_count = df.count()
        print(f"✅ Read {row_count} rows from CSV")

        # Show data
        print("\n📊 Data Preview:")
        df.show(5)

        print("\n📝 Schema:")
        df.printSchema()

        # Write to Parquet (Bronze layer)
        print("\n💾 Writing to Parquet (Bronze layer)...")
        df.write \
            .mode("overwrite") \
            .parquet("/data/bronze/events")

        print("✅ Successfully wrote to /data/bronze/events")

        # Verify by reading back
        print("\n✔️ Verifying read from Parquet...")
        df_verify = spark.read.parquet("/data/bronze/events")
        verify_count = df_verify.count()
        print(f"✅ Verified {verify_count} rows in Parquet")

        if verify_count == row_count:
            print("\n🎉 SUCCESS: CSV → Parquet transformation complete!")
            return 0
        else:
            print(f"\n❌ ERROR: Row count mismatch! CSV: {row_count}, Parquet: {verify_count}")
            return 1

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        spark.stop()

if __name__ == "__main__":
    sys.exit(main())
