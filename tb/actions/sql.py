missing_data_periods = '''

    SELECT
        tick_time,
        base,
        quot,
        runningDifference(tick_time) AS delta
    FROM
    (
        SELECT
            tick_time,
            base,
            quot
        FROM tb.ticker
        WHERE base='btc' AND quot='usd' AND tick_time >= toDateTime(1507833535) AND tick_time <= toDateTime(1515609535)
        ORDER BY tick_time ASC
    )
    WHERE delta > 600
    
    UNION ALL
    
    SELECT
        tick_time,
        base,
        quot,
        runningDifference(tick_time) AS delta
    FROM 
        frame
    ORDER BY tick_time ASC
    LIMIT 1

    UNION ALL
    
    SELECT
        tick_time,
        base,
        quot,
        runningDifference(tick_time) AS delta
    FROM 
        frame
    ORDER BY tick_time DESC
    LIMIT 1
    '''