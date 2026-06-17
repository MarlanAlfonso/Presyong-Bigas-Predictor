-- Presyong Bigas Predictor - Database Schema
-- Table: rice_prices 
-- One row = one commodity x one month x one source 

CREATE TABLE IF NOT EXISTS rice_prices (
    id              INTEGER PRIMARY KEY AUTOINCREMENT, 
    date            DATE    NOT NULL, -- EX: 2018-01-01 (first of the month)
    price_per_kg    REAL    NOT NULL, -- PHP per kg
    commodity       TEXT    NOT NULL, -- 'well_milled', 'regular_milled', 'special'
    region          TEXT    NOT NULL DEFAULT 'NCR',
    source          TEXT    NOT NULL, -- 'PSA', 'WFP'
    price_type      TEXT    NOT NULL DEFAULT 'retail',

    CONSTRAINT uq_price_record UNIQUE (date, commodity, region, source)
);

-- Indexes 
CREATE INDEX IF NOT EXISTS idx_date ON rice_prices (date);
CREATE INDEX IF NOT EXISTS idx_commodity ON rice_prices (commodity);
CREATE INDEX IF NOT EXISTS idx_source ON rice_prices (source);

-- Convenience view for the primary model series 
CREATE VIEW IF NOT EXISTS well_milled_ncr AS
SELECT date, price_per_kg
FROM rice_prices
WHERE commodity = 'well_milled'
  AND region    = 'NCR'
  AND source    = 'PSA'
ORDER BY date;