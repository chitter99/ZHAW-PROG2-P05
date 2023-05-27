from dependency_injector.wiring import Provide, inject

from .containers import Container
from . import services

@inject
def main(
    routing_service: services.RoutingService = Provide[Container.routing_service]
):
    route = routing_service.route("Bern", "Zürich")
    print(route)


if __name__ == '__main__':
    container = Container()
    main()