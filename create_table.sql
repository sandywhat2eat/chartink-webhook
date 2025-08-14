-- ChartInk Alerts Table Schema
-- Run this in your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS chartink_alerts (
    id BIGSERIAL PRIMARY KEY,
    scan_name TEXT NOT NULL,
    scan_url TEXT NOT NULL,
    alert_name TEXT NOT NULL,
    stocks TEXT[] NOT NULL,
    trigger_prices NUMERIC[] NOT NULL,
    total_stocks INTEGER NOT NULL,
    avg_trigger_price NUMERIC(10,2),
    min_trigger_price NUMERIC(10,2),
    max_trigger_price NUMERIC(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_chartink_alerts_scan_name ON chartink_alerts(scan_name);
CREATE INDEX IF NOT EXISTS idx_chartink_alerts_created_at ON chartink_alerts(created_at);
CREATE INDEX IF NOT EXISTS idx_chartink_alerts_total_stocks ON chartink_alerts(total_stocks);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_chartink_alerts_updated_at 
    BEFORE UPDATE ON chartink_alerts 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Add RLS (Row Level Security) if needed
-- ALTER TABLE chartink_alerts ENABLE ROW LEVEL SECURITY;
