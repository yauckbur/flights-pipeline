#!/usr/bin/env python
# coding: utf-8


import json
import hashlib
import pandas as pd

from pathlib import Path
from datetime import datetime


# Generate a deterministic observation ID for each row
def generate_id(row):

    record = {
        "departure_airport": row["departure_airport"],
        "arrival_airport": row["arrival_airport"],
        "outbound_date": str(row["outbound_date"]),
        "return_date": str(row["return_date"]),
        "price": int(row["price"]),
        "currency": row["currency"],
        "extraction_date": str(row["extraction_date"]),
        "flights": row["flights"]
    }

    record_string = json.dumps(
        record,
        sort_keys=True,
        default=str
    )

    return hashlib.sha256(
        record_string.encode("utf-8")
    ).hexdigest()


# Transform one SerpApi JSON response into a DataFrame
def transform_flights(data, filename):

    # Combine best and other flight itineraries
    flights = (
        (data.get("best_flights") or []) +
        (data.get("other_flights") or [])
    )

    # Return an empty DataFrame if no flights exist
    if not flights:
        return pd.DataFrame()

    # Normalise the flight itineraries
    df = pd.json_normalize(flights)

    # Extract search parameters
    params = data.get("search_parameters") or {}

    df["departure_airport"] = params.get("departure_id")
    df["arrival_airport"] = params.get("arrival_id")
    df["outbound_date"] = params.get("outbound_date")
    df["return_date"] = params.get("return_date")
    df["currency"] = params.get("currency")

    # Select required columns
    df = df[[
        "flights",
        "departure_airport",
        "arrival_airport",
        "outbound_date",
        "return_date",
        "total_duration",
        "price",
        "currency",
        "type"
    ]].copy()

    # Extract the original extraction date from filename
    # BHX_MRU_20261008_131750_217337.json
    source_file = Path(filename).name

    date_string = Path(source_file).stem.split("_")[2]

    extraction_date = datetime.strptime(
        date_string, "%Y%m%d"
    ).date()

    df["extraction_date"] = extraction_date
    df["source_file"] = source_file

    # Convert columns to appropriate data types
    df["outbound_date"] = pd.to_datetime(
        df["outbound_date"]
    ).dt.date

    df["return_date"] = pd.to_datetime(
        df["return_date"]
    ).dt.date

    df["price"] = pd.to_numeric(
        df["price"], errors="raise"
    ).astype("Int64")

    df["total_duration"] = pd.to_numeric(
        df["total_duration"], errors="coerce"
    ).astype("Int64")

    # Validate fields needed for a valid observation
    required = [
        "departure_airport",
        "arrival_airport",
        "outbound_date",
        "return_date",
        "price",
        "currency"
    ]

    if df[required].isna().any().any():
        raise ValueError(f"Missing required data in {source_file}")

    if not df["flights"].apply(
        lambda x: isinstance(x, list) and len(x) > 0
    ).all():
        raise ValueError(f"Invalid flight legs in {source_file}")

    # Number of outbound stops = number of legs - 1
    df["stops"] = df["flights"].apply(
        lambda legs: len(legs) - 1
    )

    # Generate hash before converting the nested flights
    df["observation_id"] = df.apply(
        generate_id, axis=1
    )

    # Convert nested flights into JSON-formatted strings
    df["flights"] = df["flights"].apply(
        lambda legs: json.dumps(legs, sort_keys=True)
    )

    # Arrange columns in the final order
    df = df[[
        "observation_id",
        "extraction_date",
        "departure_airport",
        "arrival_airport",
        "outbound_date",
        "return_date",
        "total_duration",
        "stops",
        "price",
        "currency",
        "type",
        "flights",
        "source_file"
    ]]

    return df
