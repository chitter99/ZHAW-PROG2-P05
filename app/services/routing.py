#!/usr/bin/env python3
""" TransportApp """

__author__ = "Aghrabi Carim, Zambelli Adrian, Schmid Aaron"
__version__ = "1.0.0"

import math
from enum import Enum
from typing import List
from geopy.geocoders import Nominatim

from .base import BaseService
from .transport import TransportService
from .foreign_providers import ForeignProvidersService
from ..models import (
    Route,
    RoutingParameters,
    RoutingConnectingStationsParams,
    Location,
    RouteLocation,
    RouteConnection,
    RouteConnectionProvider,
)
from .. import geomath


class RoutingProgressEnum(Enum):
    ROUTING_DIRECTLY = 1
    FINDING_CONNECTING_STATIONS = 2
    ROUTING_INDIRECTLY = 3


class RoutingService(BaseService):
    def __init__(
        self,
        geolocator: Nominatim,
        transport_service: TransportService,
        foreign_providers_service: ForeignProvidersService,
        steps: int,
        nearness: int,
    ) -> None:
        self.geolocator = geolocator
        self.transport = transport_service
        self.foreign_providers = foreign_providers_service
        self.steps = int(steps)
        self.nearness = int(nearness)
        super().__init__()

    def get_country(self, point):
        location = self.geolocator.reverse(f"{point[0]}, {point[1]}")
        if location and "country" in location.raw["address"]:
            return location.raw["address"]["country_code"]
        return None

    def find_connecting_stations(
        self, params: RoutingConnectingStationsParams, on_progress=None
    ) -> List[RouteLocation]:
        """Uses trigeometry to find stations in the line of sight of the start and destination"""
        start = (params.start.coordinate.x, params.start.coordinate.y)
        dest = (params.destination.coordinate.x, params.destination.coordinate.y)

        stations = []
        for i, point in enumerate(
            geomath.calculate_intermediate_coordinates(dest, start, params.steps)
        ):
            locations = self.filter_suitable_locations(
                self.transport.search_locations(
                    x=point[0], y=point[1], location_type="station"
                ),
                nearness=params.nearness,
            )

            # Optional: Report progress
            if on_progress:
                on_progress(params.steps, i + 1)

            if len(locations) == 0:
                continue

            if params.only_nearest:
                locations = [locations[0]]

            # Only have to check once for the country
            # We assume that all locations on this point are in the same country
            country = self.get_country(
                (locations[0].coordinate.x, locations[0].coordinate.y)
            )

            for location in locations:
                if len(stations) > params.stop_at:
                    if on_progress:
                        on_progress(params.steps, params.steps)
                    return stations
                stations.append(RouteLocation(country=country, **location.__dict__))
        return stations

    def find_follow_up_connections(self, start, dest):
        pass

    def filter_suitable_locations(
        self, locations: List[Location], sort=True, nearness=None
    ):
        """Filter a list of locations according to parameters"""
        filtered = []
        for location in locations:
            # Transport API is inconsistent and sometimes returns invalid locations without an ID
            if location.id is None:
                continue
            if nearness:
                if location.distance <= nearness:
                    continue
            filtered.append(location)
        if sort:
            filtered.sort(key=lambda x: x.distance or 999999)
        return filtered

    def route(self, params: RoutingParameters, callback=None):
        if callback:
            callback(RoutingProgressEnum.ROUTING_DIRECTLY)

        start_location = self.filter_suitable_locations(
            self.transport.search_locations(params.start, location_type="station")
        )[0]
        destination_location = self.filter_suitable_locations(
            self.transport.search_locations(params.destination, location_type="station")
        )[0]

        direct = self.transport.get_connections(params.start, params.destination)
        if len(direct) > 0:
            return Route(
                start=start_location,
                destination=destination_location,
                found_connection=True,
                only_direct_routes=True,
                connections=[
                    RouteConnection(**connection.__dict__) for connection in direct
                ],
            )

        def stations_on_progress(total, step):
            callback(RoutingProgressEnum.FINDING_CONNECTING_STATIONS, total, step)

        if callback:
            callback(RoutingProgressEnum.FINDING_CONNECTING_STATIONS)

        connecting_stations = self.find_connecting_stations(
            RoutingConnectingStationsParams(
                start=start_location,
                destination=destination_location,
                steps=params.steps if params.steps else self.steps,
                nearness=params.nearness if params.nearness else self.nearness,
                # TODO: Add stop_at param to config and make overrideable
                stop_at=10,
            ),
            on_progress=stations_on_progress if callback else None,
        )

        if len(connecting_stations) == 0:
            return Route(
                start=start_location,
                destination=destination_location,
                found_connection=False,
            )

        def indirect_on_progress(total, step):
            callback(RoutingProgressEnum.ROUTING_INDIRECTLY, total, step)

        if callback:
            # We send a small fractions as the current progress cannot be reset to zero
            callback(
                RoutingProgressEnum.ROUTING_INDIRECTLY, len(connecting_stations), 0.1
            )

        start_latlg = (start_location.coordinate.x, start_location.coordinate.y)
        destination_latlg = (
            destination_location.coordinate.x,
            destination_location.coordinate.y,
        )

        # Aggregation for recommendation
        best_coverage = None
        best_coverage_station = None
        best_coverage_providers = None

        countries = set()
        alternative_stations = []
        alternative_connections = []
        for i, station in enumerate(connecting_stations):
            connections = self.transport.get_connections(params.start, station.name)

            if callback:
                indirect_on_progress(len(connecting_stations), i + 1)

            if len(connections) == 0:
                continue

            countries.add(station.country)

            for connection in connections:
                alternative_latlg = (
                    connection.to.station.coordinate.x,
                    connection.to.station.coordinate.y,
                )
                coverage = geomath.calculate_coverage_percentage(
                    start_latlg, destination_latlg, alternative_latlg
                )

                providers = [
                    RouteConnectionProvider(
                        name="SBB",
                        url="https://www.sbb.ch",
                        country="Schweiz",
                        country_code="CH",
                        coverage=coverage,
                    )
                ]

                foreign_provider = self.foreign_providers.get(station.country)
                if foreign_provider:
                    providers.append(
                        RouteConnectionProvider(
                            name=foreign_provider.name,
                            url=foreign_provider.url,
                            country=foreign_provider.country,
                            country_code=foreign_provider.country_code,
                            coverage=1 - coverage,
                        )
                    )
                else:
                    providers.append(
                        RouteConnectionProvider(
                            name="Unknown",
                            url="",
                            country="",
                            country_code=station.country,
                            coverage=1 - coverage,
                        )
                    )

                if best_coverage is None or coverage > best_coverage:
                    best_coverage = coverage
                    best_coverage_station = connection.to.station.name
                    best_coverage_providers = providers

                alternative_stations.append(connection.to.station.name)
                alternative_connections.append(
                    RouteConnection(
                        direct_connection=False,
                        coverage=coverage,
                        service_end_country=station.country,
                        providers=providers,
                        **connection.__dict__,
                    )
                )

        if len(alternative_connections) == 0:
            return Route(
                start=start_location,
                destination=destination_location,
                found_connection=False,
            )

        return Route(
            start=start_location,
            destination=destination_location,
            found_connection=True,
            only_direct_routes=False,
            connecting_stations=connecting_stations,
            connections=alternative_connections,
            best_coverage=best_coverage,
            best_coverage_station=best_coverage_station,
            best_coverage_providers=best_coverage_providers,
            service_end_countries=countries,
        )
