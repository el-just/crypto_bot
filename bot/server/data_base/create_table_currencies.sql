CREATE TABLE IF NOT EXISTS ej.currencies (
    modify_date Date
    , modify_time DateTime
    , name String
    , full_name String
    , id UInt32
    , tax_fee Float64
    , min_conf UInt32
    , deposit_address String
    , is_disabled UInt8
    , is_delisted UInt8
    , is_frozen UInt8
    , imprint String
) ENGINE = MergeTree (modify_date, (modify_date, name, imprint), 8192)