from dependency_injector.wiring import Provide, inject

from .containers import Container
from . import services

@inject
def main(
    routing: services.RoutingService = Provide[Container.routing_service]
):
    route = routing.route("Bern", "Zürich")
    print(route)


def run():
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])
    
    main()

if __name__ == "__main__":
    run()
