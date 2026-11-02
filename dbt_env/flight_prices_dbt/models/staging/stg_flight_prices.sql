WITH source AS(

    SELECT *
    FROM {{ source('raw_data', 'final_flights') }}
),

renamed AS (
    SELECT
        observation_id,
        extraction_date,
        departure_airport,
        arrival_airport,
        outbound_date,
        return_date,
        total_duration AS total_duration_minutes,
        stops,
        price AS price_gbp,
        currency,
        type AS offer_type,
        flights,
        source_file
    FROM source
)

SELECT *
FROM renamed