#!/usr/bin/env python
# coding: utf-8

import click
import os
import requests
import json
from pathlib import Path
from datetime import datetime, timezone


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
def run(engine, arrival_id, outbound_date, return_date, currency, gl, hl, travel_class, adults):

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
        
        # Convert API response to Python dictionary
        data = response.json()

        # Set output directory
        output_dir = Path("data/raw")

        # Generate timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")

        # Create unique filename
        filename = f"{departure_id}_{arrival_id}_{timestamp}.json"
        file_path = output_dir / filename

        # Save JSON locally
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"Saved to {file_path}")







if __name__ == '__main__':
    run()





