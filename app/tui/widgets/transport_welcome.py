from textual.widget import Widget
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label


class TransportWelcome(Widget):
    def compose(self) -> ComposeResult:
        with Container(classes="align-center-middle"):
            yield Label("(N) Start by creating a new trip!")
