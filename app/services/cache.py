from .base import BaseService
from .transport import TransportService


class TransportCacheService(BaseService):
    def __init__(self, transport_service: TransportService) -> None:
        self.transport_service = transport_service
        super().__init__()

    def get_connections(self, start, destination):
        route = start, destination
        in_blacklist = check_blacklist(route)

        if in_blacklist == True:
            return "No connection found"
        else:
            connections = self.transport_service.get_connections(start, destination)
            is_appanded = append_blacklist(connections, route)
            if is_appanded == True:
                return "No connection found"
            else:
                print(connections["connections"])

    def append_blacklist(self, connections):
        if len(connections["connections"]) == 0:
            blacklist.append(route)
            return True
        return

    def check_blacklist(self, route):
        if route in blacklist:
            return True

        else:
            x, y = route
            route = y, x
            if route in blacklist:
                return True

        return False
