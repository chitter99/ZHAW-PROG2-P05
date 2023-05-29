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
    geolocator = providers.Singleton(Nominatim, user_agent="tbz_transport_app")

    # Services
    transport_service = providers.Singleton(
        services.TransportService, url=config.transport.url
    )
    location_autocomplet_service = providers.Singleton(
        services.LocationAutocompletService, url=config.search.url
    )
    cache_service = providers.Singleton(
        services.TransportCacheService,
        transport_service=transport_service,
        path=config.data.blacklist_connections,
    )
    key_station_service = providers.Singleton(
        services.KeyStationsService,
        transport_service=cache_service,
        home_station=config.key_stations.home_station,
        path_key_stations=config.data.key_stations,
        path_key_stations_tracking=config.data.key_stations_tracking,
    )
    foreign_providers_service = providers.Singleton(
        services.ForeignProvidersService, path=config.data.foreign_providers
    )
    routing_service = providers.Singleton(
        services.RoutingService,
        geolocator=geolocator,
        transport_service=cache_service,
        foreign_providers_service=foreign_providers_service,
        steps=config.router.steps,
        nearness=config.router.nearness,
    )
    cli_service = providers.Singleton(
        services.CLIService, routing_service=routing_service
    )

    # UI
    ui = providers.Singleton(
        tui.TransportApp,
        routing_service=routing_service,
        location_autocomplet_service=location_autocomplet_service,
        key_station_service=key_station_service,
    )
