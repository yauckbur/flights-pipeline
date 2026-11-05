WITH price_history AS (

    SELECT
        extraction_date,
        min_price_gbp,
        departure_airport,
        ROW_NUMBER() OVER (PARTITION BY extraction_date ORDER BY min_price_gbp ASC) AS ranked_min_price
    FROM {{ ref('int_daily_flight_prices') }}

),

ranked_price_history AS (

    SELECT *
    FROM price_history
    WHERE ranked_min_price = 1  
),

price_history_with_rolling_avg AS (

    SELECT 
        extraction_date,
        min_price_gbp,
        departure_airport,
        AVG(min_price_gbp) OVER (ORDER BY extraction_date ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING) AS rolling_7_observation_avg_min_price_gbp
        -- If dataset were bigger, we could also calculate a 30-day rolling average
        -- AVG(min_price_gbp) OVER (ORDER BY extraction_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS rolling_30_day_avg_min_price_gbp
    FROM ranked_price_history

)

SELECT *
FROM price_history_with_rolling_avg