import os

import requests


BASE_URL = "https://serpapi.com/search"


def get_flights(
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: str | None = None,
) -> dict:

    api_key = os.getenv("SERPAPI_API_KEY")

    if not api_key:
        raise ValueError("SERPAPI_API_KEY environment variable is not set")

    params = {
        "engine": "google_flights",
        "api_key": api_key,
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "currency": "GBP",
        "gl": "uk",
        "hl": "en",
        "travel_class": 1,
        "adults": 1,
    }

    if return_date:
        params["type"] = 1
        params["return_date"] = return_date
    else:
        params["type"] = 2

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise RuntimeError(f"SerpApi error: {data['error']}")

    return data