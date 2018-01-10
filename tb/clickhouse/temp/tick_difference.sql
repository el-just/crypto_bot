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
    WHERE base='btc' AND quot='usd'
    ORDER BY tick_time ASC
)
WHERE delta > 600

SELECT tick_time, base, quot, runningDifference(tick_time) AS delta FROM ( SELECT tick_time, base, quot FROM tb.ticker WHERE base='btc' AND quot='usd' ORDER BY tick_time ASC) WHERE delta > 600 UNION ALL SELECT tick_time, base, quot, runningDifference(tick_time) AS delta FROM tb.ticker WHERE base='btc' AND quot='usd' ORDER BY tick_time DESC LIMIT 1