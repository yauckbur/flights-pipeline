#!/usr/bin/env python
# coding: utf-8

# In[8]:


import json
import hashlib
import pandas as pd

from pathlib import Path
from datetime import datetime, timezone


# In[9]:


# Find all JSON files in the raw directory and its subdirectories
files = sorted(Path("data/raw").rglob("*.json"))

print(f"Found {len(files)} JSON files")


# In[10]:


# Create an empty list to store each file's DataFrame
dfs = []


# In[11]:


# Capture the extraction date once for this batch
extraction_date = datetime.now(timezone.utc).date()


# In[12]:


# Loop through every JSON file
for file in files:

    # Open and read the JSON file
    with open(file, "r") as f:
        data = json.load(f)

    # Extract best_flights and other_flights
    flights = (
        (data.get("best_flights") or []) +
        (data.get("other_flights") or [])
    )

    # Skip files without any flights
    if not flights:
        print(f"No flights found in {file.name}")
        continue

    # Normalise the flights into a DataFrame
    df_file = pd.json_normalize(flights)

    # Extract the search parameters from the original JSON
    params = data.get("search_parameters", {})

    # Add the search parameters as columns
    df_file["departure_airport"] = params.get("departure_id")
    df_file["arrival_airport"] = params.get("arrival_id")
    df_file["outbound_date"] = params.get("outbound_date")
    df_file["return_date"] = params.get("return_date")
    df_file["currency"] = params.get("currency")

    # Select and rearrange the columns
    df_file = df_file[[
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

    # Extract the original extraction date from the filename
    # Example: BHX_MRU_20261008_131750_217337.json

    date_string = file.stem.split("_")[2]

    extraction_date = datetime.strptime(
        date_string, "%Y%m%d"
    ).date()

    # Add extraction date to every row from this file
    df_file["extraction_date"] = extraction_date

    # Preserve the source filename for traceability
    df_file["source_file"] = file.name


    # Append this DataFrame to our list
    dfs.append(df_file)


# Combine all the individual DataFrames into one
if not dfs:
    raise ValueError("No flight records found in the JSON files")

df = pd.concat(dfs, ignore_index=True)

display(df.head())


# In[13]:


# generate unique row id

def generate_id(row):

    record = {
        "departure_airport": row["departure_airport"],
        "arrival_airport": row["arrival_airport"],
        "outbound_date": row["outbound_date"],
        "return_date": row["return_date"],
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


# Generate a hash for every row across all five files
df["observation_id"] = df.apply(generate_id, axis=1)


# In[14]:


df = df[[
    "observation_id",
    "extraction_date",
    "departure_airport",
    "arrival_airport",
    "outbound_date",
    "return_date",
    "total_duration",
    "price",
    "currency",
    "type",
    "flights",
    "source_file"
]]

display(df.head())


# In[ ]:




