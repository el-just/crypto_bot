SELECT * FROM (
    SELECT
        tick_time,
        base,
        quot,
        runningDifference(tick_time) AS delta,
        2 as tp
    FROM
    (
        SELECT
            tick_time,
            base,
            quot
        FROM tb.ticker
        WHERE base='{base}' AND quot='{quot}' AND tick_time >= toDateTime({start}) AND tick_time <= toDateTime({end})
        ORDER BY tick_time ASC
    )
    WHERE delta > {default_miss_time}

    UNION ALL

    SELECT
        tick_time,
        base,
        quot,
        runningDifference(tick_time) AS delta,
        0 as tp
    FROM tb.ticker
    WHERE base='{base}' AND quot='{quot}' AND tick_time >= toDateTime({start}) AND tick_time <= toDateTime({end})
    ORDER BY tick_time ASC
    LIMIT 1

    UNION ALL

    SELECT
        tick_time,
        base,
        quot,
        runningDifference(tick_time) AS delta,
        1 as tp
    FROM tb.ticker
    WHERE base='{base}' AND quot='{quot}' AND tick_time >= toDateTime({start}) AND tick_time <= toDateTime({end})
    ORDER BY tick_time DESC
    LIMIT 1
)

ORDER BY tp ASC, tick_time ASC

FORMAT CSVWithNames