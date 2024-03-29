#!/usr/bin/env python3
""" TransportApp """

__author__ = "Aghrabi Carim, Zambelli Adrian, Schmid Aaron"
__version__ = "1.0.0"

from dataclasses import dataclass
from typing import Optional, Any, List


@dataclass
class KeyStationTracking:
    start: str
    station: str
    reachable: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class Route:
    start: "Location"
    destination: "Location"
    found_connection: bool
    service_end_countries: Optional[List[str]] = None
    only_direct_routes: Optional[bool] = None
    connections: Optional[List["RouteConnection"]] = None
    connecting_stations: Optional[List["Location"]] = None
    best_coverage: Optional[float] = None
    best_coverage_station: Optional[str] = None
    best_coverage_providers: Optional[List["RouteConnectionProvider"]] = None


@dataclass
class RoutingParameters:
    start: str
    destination: str
    steps: Optional[int] = None
    nearness: Optional[int] = None


@dataclass
class RoutingConnectingStationsParams:
    start: "Location"
    destination: "Location"
    steps: int = 25
    nearness: int = 1000
    stop_at: int = 10
    only_nearest: bool = True


@dataclass
class Coordinates:
    type: Optional[str]
    x: Optional[float]
    y: Optional[float]


@dataclass
class Location:
    id: Optional[str]
    type: Optional[str]
    name: Optional[str]
    score: Optional[float]
    coordinate: Optional[Coordinates]
    distance: Optional[float]


@dataclass
class Prognosis:
    platform: Optional[str]
    departure: Optional[str]
    arrival: Optional[str]
    capacity1st: Optional[str]
    capacity2nd: Optional[str]


@dataclass
class Stop:
    station: Optional[Location]
    arrival: Optional[str]
    departure: Optional[str]
    delay: Optional[int]
    platform: Optional[str]
    prognosis: Optional[Prognosis]


@dataclass
class Journey:
    name: Optional[str]
    category: Optional[str]
    categoryCode: Optional[str]
    number: Optional[str]
    operator: Optional[str]
    to: Optional[str]
    passList: Optional[List[Stop]]
    capacity1st: Optional[str]
    capacity2nd: Optional[str]


@dataclass
class Section:
    journey: Optional[Journey]
    walk: Optional[str]
    departure: Optional[Stop]
    arrival: Optional[Stop]


@dataclass
class Service:
    regular: Optional[str]
    irregular: Optional[str]


@dataclass
class Connection:
    _from: Optional[Stop]
    to: Optional[Stop]
    duration: Optional[str]
    service: Optional[Service]
    products: Optional[List[str]]
    transfers: Optional[int]
    capacity1st: Optional[str]
    capacity2nd: Optional[str]
    sections: Optional[List[Section]]


@dataclass
class RouteConnection(Connection):
    direct_connection: bool = True
    coverage: float = 1
    service_end_country: str = "CH"
    providers: Optional[List["RouteConnectionProvider"]] = None


@dataclass
class RouteConnectionProvider:
    name: str
    url: str
    country: str
    country_code: str
    coverage: float


@dataclass
class RouteLocation(Location):
    country: str


@dataclass
class ForeignProvider:
    country: str
    country_code: str
    name: str
    url: str
