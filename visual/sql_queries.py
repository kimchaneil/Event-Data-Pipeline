"""SQL queries used for chart generation."""

PRODUCT_PERFORMANCE_QUERY = """
WITH latest_product_names AS (
    SELECT DISTINCT ON (product_id)
        product_id,
        product_name
    FROM event_logs
    ORDER BY product_id, event_time DESC, id DESC
),
page_views AS (
    SELECT
        product_id,
        COUNT(*) AS page_view_count
    FROM event_logs
    WHERE event_type = 'page_view'
    GROUP BY product_id
),
purchases AS (
    SELECT
        product_id,
        COUNT(*) AS purchase_count
    FROM event_logs
    WHERE event_type = 'purchase'
    GROUP BY product_id
)
SELECT
    COALESCE(pv.product_id, p.product_id) AS product_id,
    lpn.product_name,
    COALESCE(pv.page_view_count, 0) AS page_view_count,
    COALESCE(p.purchase_count, 0) AS purchase_count,
    ROUND(
        COALESCE(p.purchase_count, 0)::numeric
        / NULLIF(COALESCE(pv.page_view_count, 0), 0) * 100,
        2
    ) AS conversion_rate_percent
FROM page_views pv
FULL OUTER JOIN purchases p
    ON pv.product_id = p.product_id
LEFT JOIN latest_product_names lpn
    ON lpn.product_id = COALESCE(pv.product_id, p.product_id)
ORDER BY conversion_rate_percent DESC NULLS LAST, page_view_count DESC;
"""

REFERRER_PERFORMANCE_QUERY = """
WITH purchase_source AS (
    SELECT DISTINCT ON (p.id)
        p.id AS purchase_id,
        pv.referrer
    FROM event_logs p
    JOIN event_logs pv
      ON p.user_id = pv.user_id
     AND p.session_id = pv.session_id
     AND p.product_id = pv.product_id
    WHERE p.event_type = 'purchase'
      AND pv.event_type = 'page_view'
      AND pv.referrer IS NOT NULL
      AND pv.event_time <= p.event_time
    ORDER BY p.id, pv.event_time DESC, pv.id DESC
),
page_views AS (
    SELECT
        referrer,
        COUNT(*) AS page_view_count
    FROM event_logs
    WHERE event_type = 'page_view'
      AND referrer IS NOT NULL
    GROUP BY referrer
),
purchases AS (
    SELECT
        referrer,
        COUNT(*) AS purchase_count
    FROM purchase_source
    GROUP BY referrer
)
SELECT
    pv.referrer,
    pv.page_view_count,
    COALESCE(p.purchase_count, 0) AS purchase_count,
    ROUND(
        COALESCE(p.purchase_count, 0)::numeric
        / NULLIF(pv.page_view_count, 0) * 100,
        2
    ) AS conversion_rate_percent
FROM page_views pv
LEFT JOIN purchases p
  ON pv.referrer = p.referrer
ORDER BY conversion_rate_percent DESC, pv.page_view_count DESC;
"""

HOURLY_DISTRIBUTION_QUERY = """
SELECT
    EXTRACT(HOUR FROM event_time)::int AS event_hour,
    COUNT(*) AS total_events,
    COUNT(*) FILTER (WHERE event_type = 'page_view') AS page_view_count,
    COUNT(*) FILTER (WHERE event_type = 'purchase') AS purchase_count
FROM event_logs
GROUP BY EXTRACT(HOUR FROM event_time)
ORDER BY event_hour;
"""
