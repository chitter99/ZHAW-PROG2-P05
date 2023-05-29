#!/usr/bin/env python3
""" TransportApp """

__author__ = "Aghrabi Carim, Zambelli Adrian, Schmid Aaron"
__version__ = "1.0.0"

from datetime import datetime
import csv

from .base import BaseService
from .transport import TransportService
from .. import models


class TransportCacheService(BaseService):
    def __init__(self, transport_service: TransportService, path: str) -> None:
        super().__init__()
        self.transport_service = transport_service
        self.path = path
        self.cache = {}
        self.load_from_file()

    def load_from_file(self):
        try:
            with open(self.path, "r", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    start = row["start"]
                    dest = row["dest"]
                    self.cache.setdefault(start, {})[dest] = row["last_check"]
        except FileNotFoundError:
            self.cache = {}

    def append_blacklist(self, start, dest):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cache.setdefault(start, {})[dest] = timestamp
        self.write_to_file()

    def write_to_file(self):
        with open(self.path, "w", newline="") as file:
            fieldnames = ["start", "dest", "last_check"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for start, destinations in self.cache.items():
                for dest, last_check in destinations.items():
                    writer.writerow(
                        {"start": start, "dest": dest, "last_check": last_check}
                    )

    def check_blacklist(self, start, dest):
        if start in self.cache and dest in self.cache[start]:
            return True
        return False

    # TransportService forwarded functions

    def search_locations(self, query=None, x=None, y=None, location_type="all"):
        return self.transport_service.search_locations(query, x, y, location_type)

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
        if self.check_blacklist(departure, arrival):
            return []

        result = self.transport_service.get_connections(
            departure,
            arrival,
            via,
            date,
            time,
            is_arrival_time,
            transportations,
            limit,
            page,
            direct,
            sleeper,
            couchette,
            bike,
            accessibility,
        )

        if len(result) == 0:
            self.append_blacklist(departure, arrival)

        return result
