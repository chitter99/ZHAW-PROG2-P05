from dependency_injector.wiring import Provide, inject

from .tui import textual

from .containers import Container
from . import tui


@inject
def main(ui: tui.TransportApp = Provide[Container.ui]):
    ui.run()


def run():
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])

    main()


if __name__ == "__main__":
    run()
