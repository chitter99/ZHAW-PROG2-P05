import math
from enum import Enum
from typing import List

from .base import BaseService
from .transport import TransportService
from ..models import Route, RoutingParameters, RoutingConnectingStationsParams, Location, RouteConnection
from .. import geomath

class RoutingProgressEnum(Enum):
    ROUTING_DIRECTLY = 1,
    FINDING_CONNECTING_STATIONS = 2,
    ROUTING_INDIRECTLY = 3,
    FINDING_FOLLOW_UP_CONNECTIONS = 4

class RoutingService(BaseService):
    def __init__(self, transport_service: TransportService, steps: int, nearness: int) -> None:
        self.transport = transport_service
        self.steps = int(steps)
        self.nearness = int(nearness)
        super().__init__()

    def find_connecting_stations(self, params: RoutingConnectingStationsParams) -> List[Location]:
        """Uses trigeometry to find stations in the line of sight of the start and destination"""
        start = (params.start.coordinate.x, params.start.coordinate.y)
        dest = (params.destination.coordinate.x, params.destination.coordinate.y)

        stations = []
        for point in geomath.calculate_intermediate_coordinates(dest, start, params.steps):
            locations = self.filter_suitable_locations(
                self.transport.search_locations(x=point[0], y=point[1], location_type="station"),
                nearness=params.nearness
            )

            if len(locations) == 0:
                continue

            if params.only_nearest:
                locations = [locations[0]]

            for location in locations:
                if len(stations) > params.stop_at:
                    return stations
                stations.append(location)
        return stations

    def find_follow_up_connections(self, start, dest):
        pass

    def filter_suitable_locations(self, locations: List[Location], sort=True, nearness=None):
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
                connections=[RouteConnection(**connection.__dict__) for connection in direct]
            )

        if callback:
            callback(RoutingProgressEnum.FINDING_CONNECTING_STATIONS)

        connecting_stations = self.find_connecting_stations(RoutingConnectingStationsParams(
            start=start_location,
            destination=destination_location,
            steps=params.steps if params.steps else self.steps,
            nearness=params.nearness if params.nearness else self.nearness,
            # TODO: Add stop_at param to config and make overrideable
            stop_at=10,
        ))

        if len(connecting_stations) == 0:
            return Route(
                start=start_location,
                destination=destination_location,
                found_connection=False
            )

        if callback:
            callback(RoutingProgressEnum.ROUTING_INDIRECTLY)

        start_latlg = (start_location.coordinate.x, start_location.coordinate.y)
        destination_latlg = (destination_location.coordinate.x, destination_location.coordinate.y)

        # Aggregation for recommendation
        best_coverage = None
        best_coverage_station = None

        alternative_stations = []
        alternative_connections = []
        for station in connecting_stations:
            connections = self.transport.get_connections(params.start, station.name)
            
            if len(connections) == 0:
                continue
            
            for connection in connections:
                alternative_latlg = (
                    connection.to.station.coordinate.x, 
                    connection.to.station.coordinate.y
                    )
                coverage = geomath.calculate_coverage_percentage(
                    start_latlg,
                    destination_latlg,
                    alternative_latlg
                )

                if best_coverage is None or coverage > best_coverage:
                    best_coverage = coverage
                    best_coverage_station = connection.to.station.name

                alternative_stations.append(connection.to.station.name)
                alternative_connections.append(RouteConnection(
                    direct_connection=False,
                    coverage=coverage,
                    **connection.__dict__
                ))

        if len(alternative_connections) == 0:
            return Route(
                start=start_location,
                destination=destination_location,
                found_connection=False
            )

        if callback:
            callback(RoutingProgressEnum.FINDING_FOLLOW_UP_CONNECTIONS)

        #follow_up_connections = []
        #for connection in alternative_connections:
        #    self.find_follow_up_connections(params.start, params.dest, connection)

        return Route(
            start=start_location,
            destination=destination_location,
            found_connection=True,
            only_direct_routes=False,
            connecting_stations=connecting_stations,
            connections=alternative_connections,
            best_coverage=best_coverage,
            best_coverage_station=best_coverage_station
        )


    # TODO: Remove depricated routing fn
    def __depricated__route(self, start, dest):
        # Check if a direct route is possible
        direct = self.transport.get_connections(start, dest)
        if not direct["connections"] is None and not len(direct["connections"]) == 0:
            return Route(
                start=start,
                dest=dest,
                direct_route=True,
                found_connection=True,
                coverage=1,
                connections=direct["connections"]
            )

        start_cor = (float(direct["from"]["coordinate"]["x"]), float(direct["from"]["coordinate"]["y"]))
        dest_cor = (float(direct["to"]["coordinate"]["x"]), float(direct["to"]["coordinate"]["y"]))
        intermediate_cords = geomath.calculate_intermediate_coordinates(dest_cor, start_cor, self.steps)

        # Approach the start location from the destination until a suitable station has been found
        found_connection = False
        for cord in intermediate_cords:
            new_dest = self.transport.search_locations(x=cord[0], y=cord[1], location_type="station")

            #self.logger.debug(cord)

            if new_dest["stations"] is None or len(new_dest["stations"]) == 0:
                continue

            suitable_station = None
            for station in new_dest["stations"]:
                # Transport API is inconsistent and sometimes returns invalid stops without an ID
                if station["id"] is None:
                    continue
                if int(station["distance"]) <= self.nearness:
                    continue
                if not suitable_station is None and suitable_station["distance"] < station["distance"]:
                    continue
                suitable_station = station

            if suitable_station is None:
                continue

            new_connection = self.transport.get_connections(start, suitable_station["name"])
            if new_connection["connections"] is None or len(new_connection["connections"]) == 0:
                continue
                
            found_connection = True
            break

        if not found_connection:
            return Route(
                start=start,
                dest=dest,
                found_connection=False,
            )

        coverage = geomath.calculate_coverage_percentage(
            start_cor,
            dest_cor,
            cord
        )
        return Route(
            start=start,
            dest=dest,
            direct_route=False,
            found_connection=True,
            nearest_startion=new_connection["to"]["name"],
            coverage=coverage,
            connections=new_connection["connections"]
        )
