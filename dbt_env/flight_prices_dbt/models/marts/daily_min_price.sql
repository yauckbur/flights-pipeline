WITH daily_min_price AS (

    SELECT
        extraction_date,
        departure_airport,
        arrival_airport,
        outbound_date,
        return_date,
        currency,
        min_price_gbp

    FROM {{ ref('int_daily_flight_prices') }}

    WHERE extraction_date = CURRENT_DATE

    ORDER BY min_price_gbp ASC

    LIMIT 1
)

SELECT * FROM daily_min_price