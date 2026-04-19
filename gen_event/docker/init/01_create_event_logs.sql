CREATE TABLE IF NOT EXISTS event_logs (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID NOT NULL UNIQUE,
    event_type VARCHAR(50) NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    session_id VARCHAR(50) NOT NULL,
    page_url VARCHAR(255) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    referrer VARCHAR(100),
    device_type VARCHAR(50),
    quantity INTEGER,
    price NUMERIC(12, 2),
    currency VARCHAR(10),
    payment_method VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_event_logs_event_type
    ON event_logs (event_type);

CREATE INDEX IF NOT EXISTS idx_event_logs_event_time
    ON event_logs (event_time);

CREATE INDEX IF NOT EXISTS idx_event_logs_user_id
    ON event_logs (user_id);

CREATE INDEX IF NOT EXISTS idx_event_logs_product_id
    ON event_logs (product_id);
