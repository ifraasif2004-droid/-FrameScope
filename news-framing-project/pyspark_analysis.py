from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, length, when, udf
from pyspark.sql.types import StringType, FloatType
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Spark Session (local mode)
spark = SparkSession.builder \
    .appName("NewsFramingAnalysis") \
    .master("local[*]") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")
print("Spark Session started!")

# Load data from PostgreSQL into Spark DataFrame
DB_URL = f"jdbc:postgresql://{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
DB_PROPS = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "driver": "org.postgresql.Driver"
}

# We'll load via pandas first then convert to Spark
import pandas as pd

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

print("Loading articles from PostgreSQL...")
df_pandas = pd.read_sql("""
    SELECT 
        a.id,
        a.title,
        a.source_name,
        a.query_used,
        a.published_at,
        af.frame_label,
        af.score,
        af.is_dominant,
        at.sentiment_label,
        at.sentiment_score,
        at.intensity_label,
        at.intensity_score
    FROM articles a
    LEFT JOIN article_frames af ON a.id = af.article_id
    LEFT JOIN article_tone at ON a.id = at.article_id
    WHERE af.is_dominant = true
""", conn)
conn.close()

print(f"Loaded {len(df_pandas)} records into pandas")

# Convert to Spark DataFrame
df = spark.createDataFrame(df_pandas)
print("Converted to Spark DataFrame!")
print(f"Total records: {df.count()}")

print("\n--- ANALYSIS 1: Frame Distribution by Topic ---")
df.groupBy("query_used", "frame_label") \
  .count() \
  .orderBy("query_used", col("count").desc()) \
  .show(30, truncate=False)

print("\n--- ANALYSIS 2: Sentiment Distribution ---")
df.groupBy("sentiment_label") \
  .count() \
  .orderBy(col("count").desc()) \
  .show()

print("\n--- ANALYSIS 3: Most Sensational Topics ---")
df.groupBy("query_used", "intensity_label") \
  .count() \
  .orderBy(col("count").desc()) \
  .show(20)

print("\n--- ANALYSIS 4: Top Frames Overall ---")
df.groupBy("frame_label") \
  .count() \
  .orderBy(col("count").desc()) \
  .show()

print("\n--- ANALYSIS 5: Average Sentiment by Topic ---")
df.groupBy("query_used") \
  .avg("sentiment_score") \
  .orderBy(col("avg(sentiment_score)").desc()) \
  .show()

spark.stop()
print("\nSpark analysis complete!")