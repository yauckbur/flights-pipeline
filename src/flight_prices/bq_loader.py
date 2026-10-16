#!/usr/bin/env python
# coding: utf-8

import json
import argparse
import pandas as pd
from datetime import datetime
from google.cloud import bigquery, storage
from flight_prices.transform import transform_flights

BUCKET_NAME = "flights-pipeline-data-lake-ya"




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument ('--date', default = datetime.today().strftime('%Y-%m-%d'))

    args = parser.parse_args()

    date = args.date

    PREFIX = f"raw/flights/extraction_date={date}/"


    client_gcs = storage.Client()
    client_bq = bigquery.Client()


    #This stores a list of blob objects in the path, not the actual json contents.
    blobs = [
        blob
        for blob in client_gcs.list_blobs(BUCKET_NAME, prefix=PREFIX)
        if blob.name.endswith(".json")
        
    ]


    #download as text downloads json to memory and json.loads reads json as a python object.
    #dfs = [] creates an empty list to store your transformed DataFrames.
    #The loop downloads each JSON file into memory.
    #json.loads() converts each JSON string into a Python dictionary.
    #transform_flights(data) transforms each dictionary into a DataFrame.
    #dfs.append(df) adds each transformed DataFrame to your list.
    #pd.concat() combines everything into one DataFrame.

    dfs = []

    for blob in blobs:
        raw_json = blob.download_as_text()
        data = json.loads(raw_json)

        df = transform_flights(data, blob.name)
        dfs.append(df)


    if not dfs:
        raise ValueError(f"No JSON data found for {date}")

    df_final = pd.concat(dfs, ignore_index=True)

    
    #ensure dataframe is not empty
    if df_final.empty:
        raise ValueError("No flight observations to process.")



    #check for duplicate observation IDs or null entries
    if (
        not df_final["observation_id"].duplicated().any()
        and not df_final["observation_id"].isna().any()
    ):
        print("Validation passed. Proceeding with staging.")
    else:
        raise ValueError("Duplicate or null observation IDs found.")



    #set table id
    table_id = "flights-pipeline-510915.flights_warehouse.staging_flights"



    #create schema for the BigQuery staging table
    staging_schema = [
        bigquery.SchemaField("observation_id", "STRING"),
        bigquery.SchemaField("extraction_date", "DATE"),
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

    job_config = bigquery.LoadJobConfig(schema=staging_schema, write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED)



    load_job = client_bq.load_table_from_dataframe(
        dataframe = df_final,
        destination = table_id,
        job_config=job_config)
    load_job.result()

    print(f"Successfully loaded {load_job.output_rows} rows into staging.")



    merge_sql = """
    MERGE `flights-pipeline-510915.flights_warehouse.final_flights` AS target

    USING `flights-pipeline-510915.flights_warehouse.staging_flights` AS source

    ON target.observation_id = source.observation_id

    WHEN NOT MATCHED THEN
        INSERT (
            observation_id,
            extraction_date,
            departure_airport,
            arrival_airport,
            outbound_date,
            return_date,
            total_duration,
            stops,
            price,
            currency,
            type,
            flights,
            source_file
        )
        VALUES (
            source.observation_id,
            source.extraction_date,
            source.departure_airport,
            source.arrival_airport,
            source.outbound_date,
            source.return_date,
            source.total_duration,
            source.stops,
            source.price,
            source.currency,
            source.type,
            source.flights,
            source.source_file
        )
    """


    merge_job = client_bq.query(merge_sql)

    merge_job.result()

    print(f"MERGE completed: {merge_job.num_dml_affected_rows} rows inserted.")

if __name__ == "__main__":
    main()
