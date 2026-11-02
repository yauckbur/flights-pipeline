
WITH flight_prices AS (

    SELECT *
    FROM {{ ref('stg_flight_prices') }}

),

daily_prices AS (

    SELECT
        extraction_date,
        departure_airport,
        arrival_airport,
        outbound_date,
        return_date,
        currency,

        COUNT(*) AS offers_observed,
        MIN(price_gbp) AS min_price_gbp,
        ROUND(AVG(price_gbp), 2) AS avg_price_gbp,
        MAX(price_gbp) AS max_price_gbp

    FROM flight_prices

    WHERE currency = 'GBP'

    GROUP BY
        extraction_date,
        departure_airport,
        arrival_airport,
        outbound_date,
        return_date,
        currency

)

SELECT * FROM daily_prices
