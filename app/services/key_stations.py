#!/usr/bin/env python3
""" TransportApp """

__author__ = "Aghrabi Carim, Zambelli Adrian, Schmid Aaron"
__version__ = "1.0.0"


from datetime import datetime
import csv
from dataclasses import dataclass
from typing import List

from .base import BaseService
from .transport import TransportService
from .. import models


class KeyStationsService(BaseService):
    def __init__(
        self,
        transport_service: TransportService,
        home_station: str,
        path_key_stations: str,
        path_key_stations_tracking,
    ) -> None:
        super().__init__()
        self.transport_service = transport_service
        self.home_station = home_station
        self.path_key_stations = path_key_stations
        self.path_key_stations_tracking = path_key_stations_tracking
        self.key_stations_tracking = []
        self.key_stations = []
        self.load_from_file()

    def load_from_file(self):
        # Read key stations
        try:
            with open(self.path_key_stations, "r", newline="") as file:
                self.key_stations = file.readlines()
        except FileNotFoundError:
            self.key_stations = []

        # Read tracking file
        try:
            with open(self.path_key_stations_tracking, "r", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.key_stations_tracking.append(
                        models.KeyStationTracking(
                            start=row["start"],
                            station=row["station"],
                            reachable=bool(row["reachable"]),
                            latitude=float(row["latitude"])
                            if row["latitude"]
                            else None,
                            longitude=float(row["longitude"])
                            if row["longitude"]
                            else None,
                        )
                    )
        except FileNotFoundError:
            self.key_stations_tracking = []

    def write_to_file(self):
        with open(self.path_key_stations_tracking, "w", newline="") as file:
            fieldnames = [
                "start",
                "station",
                "reachable",
                "latitude",
                "longitude",
            ]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for tracking_entry in self.key_stations_tracking:
                writer.writerow(
                    {
                        "start": tracking_entry.start,
                        "station": tracking_entry.station,
                        "reachable": str(tracking_entry.reachable),
                        "latitude": str(tracking_entry.latitude)
                        if tracking_entry.latitude is not None
                        else "",
                        "longitude": str(tracking_entry.longitude)
                        if tracking_entry.longitude is not None
                        else "",
                    }
                )

    def refetch_tracking(self, on_progress=None) -> List[models.KeyStationTracking]:
        start = self.home_station
        tracking = []
        for i, station in enumerate(self.key_stations):
            connections = self.transport_service.get_connections(start, station)

            if on_progress:
                on_progress(len(self.key_stations), i)

            if len(connections) == 0:
                tracking.append(
                    models.KeyStationTracking(
                        start=start, station=station, reachable=False
                    )
                )
            else:
                tracking.append(
                    models.KeyStationTracking(
                        start=start,
                        station=station,
                        reachable=True,
                        latitude=connections[0].to.station.coordinate.x,
                        longitude=connections[0].to.station.coordinate.y,
                    )
                )
        self.key_stations_tracking = tracking
        self.write_to_file()
        return tracking
