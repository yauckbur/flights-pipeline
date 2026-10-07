from datetime import datetime, timedelta, timezone

from flight_prices.serpapi_client import get_flights


def extract_price_history(
    data: dict,
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: str | None = None,
) -> list[dict]:

    price_insights = data.get("price_insights", {})
    price_history = price_insights.get("price_history", [])

    if not price_history:
        raise ValueError("No price history found in SerpApi response")

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=60)

    records = []

    for timestamp, price in price_history:

        observed_at = datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc,
        )

        if observed_at < cutoff_date:
            continue

        record = {
            "observed_at": observed_at.isoformat(),
            "price": price,
            "currency": "GBP",
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "outbound_date": outbound_date,
            "return_date": return_date,
        }

        records.append(record)

    return records


if __name__ == "__main__":

    departure_ids = [
        "LHR",
        "LGW",
        "MAN",
        "BHX",
        "EDI",
    ]

    arrival_id = "MRU"

    outbound_date = "2027-01-07"
    return_date = "2027-01-16"

    all_records = []

    for departure_id in departure_ids:

        print(f"Getting price history for {departure_id} → {arrival_id}")

        data = get_flights(
            departure_id=departure_id,
            arrival_id=arrival_id,
            outbound_date=outbound_date,
            return_date=return_date,
        )

        try:
            records = extract_price_history(
                data=data,
                departure_id=departure_id,
                arrival_id=arrival_id,
                outbound_date=outbound_date,
                return_date=return_date,
            )

        except ValueError as error:
            print(f"{departure_id}: {error}")
            continue

        all_records.extend(records)

        print(
            f"{departure_id}: "
            f"{len(records)} historical price records"
        )

    print(
        f"\nTotal historical records: "
        f"{len(all_records)}"
    )

    print("\nFirst 5 records:")

    for record in all_records[:5]:
        print(record)