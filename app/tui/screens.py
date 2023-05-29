from textual.app import ComposeResult
from textual.screen import Screen
from textual.reactive import reactive
from textual.containers import Horizontal, VerticalScroll, Container
from textual.widgets import (
    Static,
    Label,
    Input,
    Button,
    Header,
    Footer,
    LoadingIndicator,
    Select,
)
from textual.worker import Worker, WorkerState

from .. import models, services
from . import widgets


class BaseScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()


class CreateNewRouteScreen(BaseScreen):
    def compose(self) -> ComposeResult:
        yield from super().compose()
        with Container(id="route-form"):
            yield Static("Create a new trip")
            yield widgets.LocationAutocompletInput(
                "Enter starting location", id="start"
            )
            yield widgets.LocationAutocompletInput(
                "Enter destination location", id="dest"
            )
            yield Button("Calculate")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.routing()

    def routing(self):
        start = self.query_one("#start Input").value
        dest = self.query_one("#dest Input").value
        if not start or not dest or start == "" or dest == "":
            return

        def callback(route):
            # We have to forward the resulting route to main app
            self.dismiss(route)

        self.app.push_screen(LoadingRoutingScreen(start=start, dest=dest), callback)


class LoadingRoutingScreen(Screen):
    def __init__(self, start, dest, name=None, id=None, classes=None) -> None:
        self.start = start
        self.dest = dest
        super().__init__(name, id, classes)

    def on_mount(self) -> None:
        self.run_worker(self.lookup_route, exclusive=True)

    def lookup_route(self) -> models.Route:
        return self.app.routing_service.route(
            models.RoutingParameters(start=self.start, destination=self.dest),
            self.routing_callback,
        )

    def routing_callback(self, state: services.RoutingProgressEnum):
        status = self.query_one("#loading-text")
        if state == services.RoutingProgressEnum.ROUTING_DIRECTLY:
            status.update("Trying direct routing")
        if state == services.RoutingProgressEnum.FINDING_CONNECTING_STATIONS:
            status.update("Findings alternative stations in")
        if state == services.RoutingProgressEnum.ROUTING_INDIRECTLY:
            status.update("Trying routing over alternative stations")
        if state == services.RoutingProgressEnum.FINDING_FOLLOW_UP_CONNECTIONS:
            status.update("Getting follow-up connections")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.state == WorkerState.SUCCESS:
            self.dismiss(event.worker.result)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Initalizing", id="loading-text")
        yield LoadingIndicator()
