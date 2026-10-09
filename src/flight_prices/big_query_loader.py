import json
import argparse
import pandas as pd
from google.cloud import bigquery, storage
from flight_prices.transform import transform_flights


client = storage.Client()

bucket = client.bucket("flights-pipeline-data-lake-ya")




#create a BigQuery client
bq_client = bigquery.Client()

#set table_id for the BigQuery table where the transformed data will be loaded
table_id = "flights-pipeline-510915.flights_warehouse.flights-transformed"

#create schema for the BigQuery table
schema = [
    bigquery.SchemaField("observation_id", "STRING"),
    bigquery.SchemaField("extraction_date", "TIMESTAMP"),
    bigquery.SchemaField("departure_airport", "STRING"),
    bigquery.SchemaField("arrival_airport", "STRING"),
    bigquery.SchemaField("outbound_date", "DATE"),
    bigquery.SchemaField("return_date", "DATE"),
    bigquery.SchemaField("total_duration", "INTEGER"),
    bigquery.SchemaField("stops", "INTEGER"),
    bigquery.SchemaField("price", "INTEGER"),
    bigquery.SchemaField("currency", "STRING"),
    bigquery.SchemaField("type", "STRING"),
    bigquery.SchemaField("flights", "STRING"),
    bigquery.SchemaField("source_file", "STRING"),
  
]

#create job config for the BigQuery load job
job_config = bigquery.LoadJobConfig(
    schema=schema,
    skip_leading_rows=1,
    source_format=bigquery.source_format.csv)




