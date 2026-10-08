#!/usr/bin/env python
# coding: utf-8

import click
import os
import requests
from datetime import datetime, timezone
from google.cloud import storage


BASE_URL = "https://serpapi.com/search"

api_key = os.getenv("SERPAPI_API_KEY")
if not api_key:
    raise ValueError("SERPAPI_API_KEY environment variable is missing")

departure_airports = ['LHR', 'LGW', 'MAN', 'BHX', 'STN']


@click.command()
@click.option('--engine', default='google_flights', help='SERPAPI engine')
@click.option('--arrival_id', default='MRU', help='destination airport code')
@click.option('--outbound_date', type=click.DateTime(formats=['%Y-%m-%d']), default='2027-01-07', help='departure date')
@click.option('--return_date', type=click.DateTime(formats=['%Y-%m-%d']), default='2027-01-16', help='return date')
@click.option('--currency', default='GBP', help='currency')
@click.option('--gl', default='uk', help='location')
@click.option('--hl', default='en', help='language')
@click.option('--travel_class', default= 1, type = click.IntRange(1,4), help='select travel class, 1 = economy 2 = premium economy 3 = business 4 = first')
@click.option('--adults', default = 2, type = click.IntRange(min=1), help = 'number of adults travelling')
@click.option('--gcs_bucket', default='flights-pipeline-data-lake-ya', help='GCS bucket name')
@click.option('--gcs_path', default='raw/flights', help='GCS path to store the data')
def run(engine, arrival_id, outbound_date, return_date, currency, gl, hl, travel_class, adults, gcs_bucket, gcs_path):

    storage_client = storage.Client()
    bucket =storage_client.bucket(gcs_bucket)

    for departure_id in departure_airports:

        params = {
            "engine": engine,
            "api_key": api_key,
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "outbound_date": outbound_date.strftime('%Y-%m-%d'),
            "return_date": return_date.strftime('%Y-%m-%d'),
            "currency": currency,
            "gl": gl,
            "hl": hl,
            "travel_class": travel_class,
            "adults": adults,
        }

        print(f"Getting flights for {departure_id} -> {arrival_id}")

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        # Generate extraction timestamp
        extraction_at = datetime.now(timezone.utc)

        # Extraction date for folder
        extraction_date = extraction_at.strftime("%Y-%m-%d")

        

        # Generate timestamp for file name
        timestamp = extraction_at.strftime("%Y%m%d_%H%M%S_%f")

        # Create unique filename
        filename = f"{departure_id}_{arrival_id}_{timestamp}.json"

        #define GCS object path
        blob = bucket.blob(f"{gcs_path}/extraction_date={extraction_date}/{filename}")

        # Upload JSON directly to GCS
        blob.upload_from_string(
            response.content,
            content_type="application/json"
        )


        print(f"Uploaded to gs://{bucket.name}/{blob.name}")




if __name__ == '__main__':
    run()





