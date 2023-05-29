from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer


class BaseScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
