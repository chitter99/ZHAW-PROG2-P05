from dependency_injector.wiring import Provide, inject

from .containers import Container
from . import services

@inject
def main(
    cli: services.CLIService = Provide[Container.cli_service]
):
    cli.run()


def run():
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])

    main()

if __name__ == "__main__":
    run()
