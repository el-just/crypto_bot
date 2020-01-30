ALTER TABLE tb.ticker MODIFY COLUMN base Enum8 ( 'usd' = 0, 'btc' = 1, 'eth' = 2, 'ltc' = 3, 'etc' = 4, 'rrt' = 5, 'zec' = 6, 'xmr' = 7, 'dsh' = 8, 'xrp' = 9, 'iot' = 10, 'eos' = 11, 'san' = 12, 'omg' = 13, 'bch' = 14, 'neo' = 15, 'etp' = 16, 'qtm' = 17, 'avt' = 18, 'edo' = 19, 'btg' = 20, 'dat' = 21, 'qsh' = 22, 'yyw' = 23, 'gnt' = 24, 'snt' = 25, 'bat' = 26, 'mna' = 27, 'fun' = 28, 'zrx' = 29, 'tnb' = 30, 'spk' = 31 )

CREATE TABLE tb.ticker (
	tick_date Date,
	tick_time DateTime,

	base Enum8 ('usd' = 0, 'btc' = 1, 'eth' = 2, 'ltc' = 3, 'etc' = 4, 'rrt' = 5, 'zec' = 6, 'xmr' = 7, 'dsh' = 8, 'xrp' = 9, 'iot' = 10, 'eos' = 11, 'san' = 12, 'omg' = 13, 'bch' = 14, 'neo' = 15, 'etp' = 16, 'qtm' = 17, 'avt' = 18, 'edo' = 19, 'btg' = 20, 'dat' = 21, 'qsh' = 22, 'yyw' = 23, 'gnt' = 24, 'snt' = 25, 'bat' = 26, 'mna' = 27, 'fun' = 28, 'zrx' = 29, 'tnb' = 30, 'spk' = 31),
	quot Enum8 ('usd' = 0, 'btc' = 1, 'eth' = 2),

	close Float64,
	volume Float64
) ENGINE = MergeTree (tick_date, (tick_time, base, quot), 8192)

INSERT INTO tb.ticker VALUES (toDate({timestamp}), toDateTime({timestamp}), {base}, {quot}, {close}, {volume})