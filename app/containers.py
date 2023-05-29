from dependency_injector import containers, providers
import logging.config
from geopy.geocoders import Nominatim

from . import services, tui


class Container(containers.DeclarativeContainer):
    config = providers.Configuration(ini_files=["config.ini"])
    logging = providers.Resource(
        logging.config.fileConfig,
        fname="logging.ini",
    )

    # Geolocator
    geolocator = providers.Singleton(Nominatim, user_agent="my_app")

    # Services
    transport_service = providers.Singleton(
        services.TransportService, url=config.transport.url
    )
    location_autocomplet_service = providers.Singleton(
        services.LocationAutocompletService, url=config.search.url
    )
    cache_service = providers.Singleton(
        services.TransportCacheService, transport_service=transport_service
    )
    routing_service = providers.Singleton(
        services.RoutingService,
        geolocator=geolocator,
        transport_service=transport_service,
        steps=config.router.steps,
        nearness=config.router.nearness,
    )
    cli_service = providers.Singleton(
        services.CLIService, routing_service=routing_service
    )
    foreign_providers_service = providers.Singleton(
        services.ForeignProvidersService, path=config.data.foreign_providers
    )

    # UI
    ui = providers.Singleton(
        tui.TransportApp,
        routing_service=routing_service,
        location_autocomplet_service=location_autocomplet_service,
        foreign_providers_service=foreign_providers_service,
    )
