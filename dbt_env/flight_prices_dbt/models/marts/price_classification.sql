
WITH price_classification AS (

    SELECT
        extraction_date,
        min_price_gbp,
        departure_airport,
        rolling_7_observation_avg_min_price_gbp,

        CASE
            WHEN rolling_7_observation_avg_min_price_gbp IS NULL
                THEN 'Insufficient History'

            WHEN min_price_gbp < rolling_7_observation_avg_min_price_gbp
                THEN 'Below Average'

            WHEN min_price_gbp > rolling_7_observation_avg_min_price_gbp
                THEN 'Above Average'

            ELSE 'Average'

        END AS price_category

    FROM {{ ref('price_history') }}

    WHERE extraction_date = CURRENT_DATE()

)

SELECT *
FROM price_classification
