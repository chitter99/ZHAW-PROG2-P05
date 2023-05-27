import math

from .base import BaseService
from .transport import TransportService
from ..models import Route

class RoutingService(BaseService):
    def __init__(self, transport_service: TransportService, step_factor: int, nearness: float) -> None:
        self.transport = transport_service
        self.step_factor = step_factor
        super().__init__()

    def calculate_coverage(self, start, dest, reached) -> float:
        total_distance = math.sqrt((dest[0] - start[0]) ** 2 + (dest[1] - start[1]) ** 2)
        current_distance = math.sqrt((reached[0] - start[0]) ** 2 + (reached[1] - start[1]) ** 2)
        return current_distance / total_distance

    def route(self, start, dest):
        # Check if a direct route is possible
        direct = self.transport.get_connections(start, dest)
        if direct["connections"] is not None:
            return Route(
                start=start,
                dest=dest,
                direct_route=True,
                coverage=1,
                connections=direct["connections"]
            )

        # Approach the start location from the destination until a station has been found
        x_step = abs(direct["from"]["coordinate"]["x"] - direct["to"]["coordinate"]["x"]) / self.step_factor
        y_step = abs(direct["from"]["coordinate"]["y"] - direct["to"]["coordinate"]["y"]) / self.step_factor
        near_loc = (direct["to"]["coordinate"]["x"], direct["to"]["coordinate"]["y"])

        found_connection = False
        while not found_connection:
            near_loc = (near_loc[0] - x_step, near_loc[1] - y_step)
            new_dest = self.transport.search_locations(x=near_loc[0], y=near_loc[1])

            if new_dest["stations"] is None:
                continue

            # TODO: Implement nearness (~20 grad)

            new_connection = self.transport.get_connections(start, new_dest["stations"][0]["name"])
            if direct["connections"] is None:
                continue
                
            found_connection = True

        return Route(
            start=start,
            dest=dest,
            direct_route=False,
            nearest_startion=new_connection["to"]["name"],
            coverage=self.calculate_coverage(
                (direct["from"]["coordinate"]["x"], direct["from"]["coordinate"]["y"]),
                (direct["to"]["coordinate"]["x"], direct["to"]["coordinate"]["y"]),
                near_loc
            ),
            connections=new_connection["connections"]
        )

