from dataclasses import dataclass
from typing import Optional, Any, List

@dataclass
class Route:
    start: "Location"
    destination: "Location"
    found_connection: bool
    only_direct_routes: Optional[bool] = None
    connections: Optional[List["RouteConnection"]] = None
    connecting_stations: Optional[List["Location"]] = None
    best_coverage: Optional[float] = None
    best_coverage_station: Optional[str] = None

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
