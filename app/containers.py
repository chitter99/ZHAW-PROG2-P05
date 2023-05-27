from dependency_injector import containers, providers
import logging.config

from . import services

class Container(containers.DeclarativeContainer):
    config = providers.Configuration(ini_files=["config.ini"])
    logging = providers.Resource(
        logging.config.fileConfig,
        fname="logging.ini",
    )

    # Services
    transport_service = providers.Singleton(
        services.TransportService,
        url=config.transport.url
    )
    routing_service = providers.Singleton(
        services.RoutingService,
        transport_service=transport_service,
        steps=config.router.steps,
        nearness=config.router.nearness
    )
    cli_service = providers.Singleton(
        services.CLIService,
        routing_service=routing_service
    )
