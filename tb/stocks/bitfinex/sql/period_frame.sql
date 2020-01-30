SELECT
    *
FROM
    tb.ticker
WHERE
    base='{base}' AND quot='{quot}' AND tick_time >= toDateTime({start}) AND tick_time <= toDateTime({end})
ORDER BY tick_time ASC

FORMAT CSVWithNames