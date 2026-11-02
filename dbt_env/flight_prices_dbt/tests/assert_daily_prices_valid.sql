SELECT *
FROM {{ ref('int_daily_flight_prices') }}

WHERE
    min_price_gbp <= 0
    OR min_price_gbp > avg_price_gbp
    OR avg_price_gbp > max_price_gbp
    OR offers_observed <= 0