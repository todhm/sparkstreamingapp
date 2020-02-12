import logging
import os 
import json
from pyspark.sql import SparkSession
from pyspark.sql.types import *
import pyspark.sql.functions as psf
from pyspark.sql.window import Window


schema = StructType([
    StructField('crime_id', StringType()),
    StructField('original_crime_type_name', StringType()),
    StructField('report_date', StringType()),
    StructField('call_date', StringType()),
    StructField('offense_date', StringType()),
    StructField('call_time', StringType()),
    StructField('call_date_time', StringType()),
    StructField('disposition', StringType()),
    StructField('address', StringType()),
    StructField('city', StringType(), True),
    StructField('state', StringType()),
    StructField('agency_id', StringType()),
    StructField('address_type', StringType()),
    StructField('common_location', StringType(), True)
])

def run_spark_job(spark):

    # TODO Create Spark Configuration
    # Create Spark configurations with max offset of 200 per trigger
    # set up correct bootstrap server and port
    BROKER_URL = os.environ.get("BROKER_URL")
    kafka_url = os.environ.get("KAFKA_BOOSTRAP_SERVER_NAME",'kafka')
    kafka_port = os.environ.get("KAFKA_BOOSTRAP_SERVER_PORT",'9092')
    df = spark \
        .readStream \
        .format("kafka")\
        .option('kafka.bootstrap.servers','kafka:19092')\
        .option("startingOffsets", "earliest") \
        .option("maxOffsetPerTrigger", "200") \
        .option("maxRatePerPartition","1000")\
        .option('spark.default.parallelism',"20")\
        .option("subscribe",'kafkapython.kafka_server.sfcrime')\
        .option("stopGracefullyOnShutdown", "true") \
        .load()

    # Show schema for the incoming resources for checks
    # TODO extract the correct column from the kafka input resources
    # Take only value and convert it to String
    kafka_df = df.selectExpr(
        'CAST(timestamp AS STRING) as timestamp',
        "CAST(value AS string) as value"
    )

    service_table = kafka_df\
        .select(psf.from_json(psf.col('value').cast("string"), schema).alias("DF"))\
        .select("DF.*")

    # TODO select original_crime_type_name and disposition
    w = Window.partitionBy("group_by").orderBy("call_date_time")
    distinct_table = service_table.select("original_crime_type_name",'disposition',psf.to_timestamp('call_date_time').alias('call_date_time'))

    # count the number of original crime type
    # aggreagte data and show those data in each time windows
    agg_df = distinct_table\
        .groupBy(
            distinct_table.original_crime_type_name,
            psf.window('call_date_time','10 minutes').alias("call_time_windows")
        )\
        .count()\
        .orderBy(psf.col('call_time_windows').desc())

    # TODO Q1. Submit a screen shot of a batch ingestion of the aggregation
    # TODO write output stream
    query = agg_df \
        .writeStream\
        .format('console')\
        .outputMode('complete')\
        .trigger(processingTime='10 seconds')\
        .start()


    # TODO attach a ProgressReporter
    query.awaitTermination()

    # # TODO get the right radio code json path
    radio_code_json_filepath = "/app/datacollections/radio_code.json"
    radio_code_df = spark.read.option("multiline","true").json(radio_code_json_filepath)
    radio_code_df.printSchema()

    # # clean up your data so that the column names match on radio_code_df and agg_df
    # # we will want to join on the disposition code

    # # TODO rename disposition_code column to disposition
    radio_code_df = radio_code_df.withColumnRenamed("disposition_code", "disposition")

    # # TODO join on disposition column
    join_query = agg_df.join(radio_code_df,'disposition')


    join_query.awaitTermination()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    # TODO Create Spark in Standalone mode
    spark = SparkSession \
        .builder \
        .master("spark://spark-master:7077") \
        .config("spark.driver.cores","2")\
        .config("spark.num.executors","2")\
        .config("spark.executor.cores","2")\
        .config("spark.driver.memory", "4g")\
        .config("spark.executor.memory", "4g")\
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.4")\
        .appName("StructuredStreamingSetup") \
        .getOrCreate()
    logger.info("Spark started")

    run_spark_job(spark)

    spark.stop()
