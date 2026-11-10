
import os
import smtplib

from datetime import datetime
from zoneinfo import ZoneInfo
from email.message import EmailMessage

from google.cloud import bigquery


# Configuration
PROJECT_ID = "flights-pipeline-510915"
DATASET = "flights_warehouse"

EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_TO = os.environ["EMAIL_TO"]
EMAIL_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]

# Today's date (UK time)
today = datetime.now(
    ZoneInfo("Europe/London")
).date()


# Connect to BigQuery
client = bigquery.Client(project=PROJECT_ID)

query = f"""
SELECT *
FROM `{PROJECT_ID}.{DATASET}.price_classification`
WHERE extraction_date = @extraction_date
ORDER BY min_price_gbp ASC
LIMIT 1
"""

job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter(
            "extraction_date", "DATE", today
        )
    ]
)

results = list(
    client.query(
        query,
        job_config=job_config,
        location="europe-west2"
    ).result()
)

if not results:
    raise RuntimeError(
        f"No flight prices available for {today}"
    )

# Extract cheapest flight
flight = dict(results[0].items())

price = flight["min_price_gbp"]
category = flight["price_category"]
airport = flight.get("departure_airport")

if price is None:
    raise RuntimeError("Cheapest flight price is missing")


# Format email
airport_line = (
    f"Departure airport: {airport}\n"
    if airport
    else ""
)

body = f"""
DAILY FLIGHT PRICE REPORT
Date: {today}

UK → Mauritius
Outbound: 7 January 2027
Return: 16 January 2027
Passengers: 2 adults

CHEAPEST FLIGHT TODAY

Price: £{float(price):,.0f}
{airport_line}Price classification: {category}

This is the cheapest observed flight across:
LHR, LGW, MAN, BHX and STN.

Source: Google Flights via SerpAPI
"""

# Create email
message = EmailMessage()

message["Subject"] = (
    f"Flight Price Report - £{float(price):,.0f} - {today}"
)

message["From"] = EMAIL_FROM
message["To"] = EMAIL_TO
message.set_content(body.strip())


# Send email
with smtplib.SMTP_SSL(
    "smtp.gmail.com", 465, timeout=30
) as smtp:

    smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
    smtp.send_message(message)

print("Daily flight price email sent successfully")
