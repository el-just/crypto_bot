CREATE TABLE IF NOT EXISTS ej.currencies (
	modify_date Date
	, modify_time DateTime
	, name String
	, full_name String
	, id UInt32
	, tax_fee Float64
	, min_conf UInt32
	, deposit_address String
	, is_disabled Boolean
	, is_delisted Boolean
	, is_frozen Boolean
	, imprint String
) ENGINE = MergeTree (modify_date, (modify_date, name, imprint), 8192)