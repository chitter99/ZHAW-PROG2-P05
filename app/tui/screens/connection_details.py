from textual.app import ComposeResult

from .base import BaseScreen
from .. import widgets
from ... import models


class ConnectionDetailsScreen(BaseScreen):
    def __init__(
        self, connection: models.RouteConnection, name=None, id=None, classes=None
    ) -> None:
        self.connection = connection
        super().__init__(name, id, classes)

    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield widgets.ConnectionOverviewWidget(self.connection)
        yield widgets.ConnectionSectionsWidget(self.connection)
