from textual.app import ComposeResult
from textual.widgets import Label, ProgressBar, Button
from textual.screen import Screen
from textual.widgets import Header
from textual.containers import Center, Middle
from textual.worker import Worker, WorkerState

from ... import models, services


class LoadingRoutingScreen(Screen):
    def __init__(self, start, dest, name=None, id=None, classes=None) -> None:
        self.start = start
        self.dest = dest
        super().__init__(name, id, classes)

    def on_mount(self) -> None:
        self.run_worker(self.lookup_route, exclusive=True, exit_on_error=False)

    def lookup_route(self) -> models.Route:
        return self.app.routing_service.route(
            models.RoutingParameters(start=self.start, destination=self.dest),
            self.routing_callback,
        )

    def routing_callback(
        self, state: services.RoutingProgressEnum, total=None, progress=None
    ):
        status = self.query_one("#loading-text")
        if state == services.RoutingProgressEnum.ROUTING_DIRECTLY:
            status.update("Trying direct routing")
        if state == services.RoutingProgressEnum.FINDING_CONNECTING_STATIONS:
            status.update("Findings alternative stations")
        if state == services.RoutingProgressEnum.ROUTING_INDIRECTLY:
            status.update("Routing over alternative stations")
        if total and progress:
            self.query_one(ProgressBar).update(total=total, progress=progress)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.state == WorkerState.SUCCESS:
            self.dismiss(event.worker.result)
        if event.state == WorkerState.ERROR:
            # TODO: We need to use this pattern due to this bug https://github.com/Textualize/textual/issues/2650
            def callback(route):
                # We have to forward the resulting route to main app
                self.dismiss(route)

            self.app.push_screen(
                LoadingRoutingErrorScreen(start=self.start, dest=self.dest), callback
            )

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Middle():
                yield Label("Initalizing", id="loading-text")
                yield ProgressBar()


class LoadingRoutingErrorScreen(Screen):
    def __init__(self, start, dest, name=None, id=None, classes=None) -> None:
        self.start = start
        self.dest = dest
        super().__init__(name, id, classes)

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Middle():
                yield Label("Something went wrong!")
                yield Label(
                    f"Due to a unknown reason the connection between {self.start} and {self.dest} could not be fetched"
                )
                yield Label("Please retry later..")
                yield Button("Back!")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(None)
