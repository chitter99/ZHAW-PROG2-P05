from textual.app import ComposeResult
from textual.widgets import Label, Button
from textual.containers import Container

from .base import BaseScreen
from .loading_routing import LoadingRoutingScreen
from .. import widgets


class CreateNewRouteScreen(BaseScreen):
    def compose(self) -> ComposeResult:
        # yield from super().compose()
        yield widgets.LocationAutocompleteInput("Enter starting location", id="start")
        yield widgets.LocationAutocompleteInput("Enter destination location", id="dest")
        yield Button("Calculate")

    def on_mount(self) -> None:
        self.border_title = "Starting new trip"
        self.styles.border_title_align = "center"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.routing()

    def routing(self):
        start = self.query_one("#start Input").value
        dest = self.query_one("#dest Input").value
        if not start or not dest or start == "" or dest == "":
            return

        # TODO: We need to use this pattern due to this bug https://github.com/Textualize/textual/issues/2650
        def callback(route):
            # We have to forward the resulting route to main app
            self.dismiss(route)

        self.app.push_screen(LoadingRoutingScreen(start=start, dest=dest), callback)
