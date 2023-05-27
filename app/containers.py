from dependency_injector import containers, providers
import logging.config

from . import services

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            services
        ],
    )

    config = providers.Configuration(ini_files=["config.ini"])
    logging = providers.Resource(
        logging.config.fileConfig,
        fname="logging.ini",
    )

    # Services
    transport_service = providers.Factory(
        services.TransportService,
        url=config.transport.url
    )    
    routing_service = providers.Factory(
        services.RoutingService,
        transport=transport_service,
        step_factor=config.router.step_factor,
        nearness=config.router.nearness
    )
