import math

from .base import BaseService
from .transport import TransportService
from ..models import Route
from .. import geomath

class RoutingService(BaseService):
    def __init__(self, transport_service: TransportService, steps: int, nearness: int) -> None:
        self.transport = transport_service
        self.steps = int(steps)
        self.nearness = int(nearness)
        super().__init__()

    def route(self, start, dest):
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

