"""Tests for PostgreSQL storage row mapping."""

from datetime import datetime
import unittest
import uuid

from gen_event.producer.event_service import build_page_view_event, build_purchase_event
from gen_event.storage.postgres import _build_insert_row


class PostgresStorageTest(unittest.TestCase):
    def test_page_view_row_mapping(self) -> None:
        event = build_page_view_event()
        row = _build_insert_row(event)

        self.assertIsInstance(row["event_id"], uuid.UUID)
        self.assertIsInstance(row["event_time"], datetime)
        self.assertEqual(row["event_type"], "page_view")
        self.assertIsNone(row["quantity"])
        self.assertIsNone(row["payment_method"])

    def test_purchase_row_mapping(self) -> None:
        event = build_purchase_event()
        row = _build_insert_row(event)

        self.assertEqual(row["event_type"], "purchase")
        self.assertIsNotNone(row["quantity"])
        self.assertIsNotNone(row["payment_method"])


if __name__ == "__main__":
    unittest.main()
