"""Tests for commerce event generation."""

from datetime import datetime, timedelta, timezone
import unittest

from gen_event.producer.event_service import build_event_time, build_page_view_event, build_purchase_event, build_random_events


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

    def test_random_batch_size(self) -> None:
        events = build_random_events(5)
        self.assertEqual(len(events), 5)

    def test_event_time_is_recent_utc_datetime(self) -> None:
        event_time = datetime.fromisoformat(build_event_time())
        now = datetime.now(timezone.utc)

        self.assertIsNotNone(event_time.tzinfo)
        self.assertLessEqual(event_time, now)
        self.assertGreaterEqual(event_time, now.replace(microsecond=0) - timedelta(days=7))


if __name__ == "__main__":
    unittest.main()
