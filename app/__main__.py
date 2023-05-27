from dependency_injector.wiring import Provide, inject

from .containers import Container
from . import services

@inject
def main(
    cache: services.TransportCacheService = Provide[Container.cache_service]
):
    cache = cache.get_connections("Bern","Amsterdam")
    print(cache)


def run():
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])
    
    main()

if __name__ == "__main__":
    run()
