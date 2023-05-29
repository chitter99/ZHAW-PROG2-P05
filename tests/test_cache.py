#!/usr/bin/env python3
""" TransportApp """

__author__ = "Aghrabi Carim, Zambelli Adrian, Schmid Aaron"
__version__ = "1.0.0"

import unittest
import csv
from datetime import datetime
from unittest.mock import MagicMock

from app.services import TransportCacheService


class MockTransportService:
    def search_locations(self, query=None, x=None, y=None, location_type="all"):
        pass

    def get_connections(
        self,
        departure,
        arrival,
        via=None,
        date=None,
        time=None,
        is_arrival_time=None,
        transportations=None,
        limit=None,
        page=None,
        direct=None,
        sleeper=None,
        couchette=None,
        bike=None,
        accessibility=None,
    ):
        pass


class TransportCacheServiceTests(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_cache.csv"
        self.cache_service = TransportCacheService(
            MockTransportService(), self.test_file
        )

    def tearDown(self):
        # Clean up the test cache file
        with open(self.test_file, "w") as file:
            file.truncate()

    def test_load_from_file(self):
        # Create a mock CSV file
        csv_data = [
            {"start": "A", "dest": "B", "last_check": "2023-01-01 12:00:00"},
            {"start": "B", "dest": "C", "last_check": "2023-01-02 12:00:00"},
        ]
        with open(self.test_file, "w", newline="") as file:
            fieldnames = ["start", "dest", "last_check"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)

        # Load cache from the file
        self.cache_service.load_from_file()

        # Verify that the cache is loaded correctly
        self.assertEqual(
            self.cache_service.cache,
            {
                "A": {"B": "2023-01-01 12:00:00"},
                "B": {"C": "2023-01-02 12:00:00"},
            },
        )

    def test_append_blacklist(self):
        # Append an entry to the cache
        self.cache_service.append_blacklist("A", "B")

        # Verify that the entry is added to the cache
        self.assertEqual(
            self.cache_service.cache,
            {
                "A": {"B": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            },
        )

        # Verify that the cache is written to the file
        with open(self.test_file, "r", newline="") as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["start"], "A")
            self.assertEqual(rows[0]["dest"], "B")

    def test_check_blacklist(self):
        # Add an entry to the cache
        self.cache_service.cache = {
            "A": {"B": "2023-01-01 12:00:00"},
            "B": {"C": "2023-01-02 12:00:00"},
        }

        # Check if the entry is in the blacklist
        self.assertTrue(self.cache_service.check_blacklist("A", "B"))

        # Check if a non-existent entry is in the blacklist
        self.assertFalse(self.cache_service.check_blacklist("A", "C"))

    def test_search_locations(self):
        # Mock the transport service and return a predefined result
        self.cache_service.transport_service.search_locations = MagicMock(
            return_value=["Location A", "Location B"]
        )

        # Call the method under test
        result = self.cache_service.search_locations(query="test")

        # Verify the result
        self.assertEqual(result, ["Location A", "Location B"])
        self.cache_service.transport_service.search_locations.assert_called_once_with(
            query="test", x=None, y=None, location_type="all"
        )

    def test_get_connections(self):
        # Mock the transport service and return a predefined result
        self.cache_service.transport_service.get_connections = MagicMock(
            return_value=["Connection A", "Connection B"]
        )

        # Call the method under test
        result = self.cache_service.get_connections("A", "B")

        # Verify the result
        self.assertEqual(result, ["Connection A", "Connection B"])
        self.cache_service.transport_service.get_connections.assert_called_once_with(
            "A",
            "B",
            via=None,
            date=None,
            time=None,
            is_arrival_time=None,
            transportations=None,
            limit=None,
            page=None,
            direct=None,
            sleeper=None,
            couchette=None,
            bike=None,
            accessibility=None,
        )

        # Verify that the entry is added to the blacklist when the result is empty
        self.cache_service.transport_service.get_connections = MagicMock(
            return_value=[]
        )
        self.cache_service.append_blacklist = MagicMock()
        result = self.cache_service.get_connections("A", "B")
        self.cache_service.append_blacklist.assert_called_once_with("A", "B")
