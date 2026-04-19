"""Tests for commerce event generation."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch
import unittest

from gen_event.producer.event_service import (
    REFERRER_PURCHASE_RATES,
    build_event_time,
    build_page_view_event,
    build_purchase_event,
    build_random_events,
    should_convert_to_purchase,
)


class EventServiceTest(unittest.TestCase):
    def test_page_view_event_fields(self) -> None:
        event = build_page_view_event()
        self.assertEqual(event["event_type"], "page_view")
        self.assertIn("product_id", event)
        self.assertIn("referrer", event)
        self.assertIn("device_type", event)

    def test_purchase_event_fields(self) -> None:
        event = build_purchase_event()
        self.assertEqual(event["event_type"], "purchase")
        self.assertIn("quantity", event)
        self.assertIn("price", event)
        self.assertIn("payment_method", event)

    def test_purchase_event_can_follow_page_view_context(self) -> None:
        page_view = build_page_view_event()
        purchase = build_purchase_event(page_view)

        self.assertEqual(purchase["user_id"], page_view["user_id"])
        self.assertEqual(purchase["session_id"], page_view["session_id"])
        self.assertEqual(purchase["product_id"], page_view["product_id"])
        self.assertGreaterEqual(
            datetime.fromisoformat(purchase["event_time"]),
            datetime.fromisoformat(page_view["event_time"]),
        )

    def test_random_batch_size(self) -> None:
        events = build_random_events(50)
        self.assertEqual(len(events), 50)

    def test_event_time_is_recent_utc_datetime(self) -> None:
        event_time = datetime.fromisoformat(build_event_time())
        now = datetime.now(timezone.utc)

        self.assertIsNotNone(event_time.tzinfo)
        self.assertLessEqual(event_time, now)
        self.assertGreaterEqual(event_time, now.replace(microsecond=0) - timedelta(days=7))

    def test_should_convert_to_purchase_uses_referrer_rate(self) -> None:
        page_view = build_page_view_event()
        page_view["referrer"] = "email"

        with patch("gen_event.producer.event_service.random.random", return_value=0.20):
            self.assertTrue(should_convert_to_purchase(page_view))

        with patch("gen_event.producer.event_service.random.random", return_value=0.50):
            self.assertFalse(should_convert_to_purchase(page_view))

    def test_referrer_purchase_rates_are_defined_for_all_referrers(self) -> None:
        page_view = build_page_view_event()
        self.assertIn(page_view["referrer"], REFERRER_PURCHASE_RATES)


if __name__ == "__main__":
    unittest.main()
