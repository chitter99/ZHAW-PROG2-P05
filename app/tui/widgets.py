import math
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, Static, Label, ListView, ListItem, DataTable
from textual.containers import Horizontal, Vertical, Container
from textual_autocomplete import AutoComplete, Dropdown, DropdownItem, InputState

from .. import models, utils

class TransportWelcome(Widget):
    def compose(self) -> ComposeResult:
        with Container(classes="align-center-middle"):
            yield Label("(N) Start by creating a new trip!")


class LocationAutocompletInput(Widget):
    def __init__(self, placeholder, *children: Widget, name = None, id = None, classes = None, disabled = False) -> None:
        self.placeholder = placeholder
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)

    def compose(self) -> ComposeResult:
        yield AutoComplete(
            Input(placeholder=self.placeholder),
            Dropdown(items=self.get_locations),
            id="search-container"
        )

    def get_locations(self, input_state: InputState) -> list[DropdownItem]:
        # TODO: Add timeout for this method to reduce network requests
        completions = self.app.location_autocomplet_service.search_completion(input_state.value)
        items = []
        for completion in completions:
            if "label" in completion:
                items.append(DropdownItem(completion["label"]))
        return items

class RouteWidget(Widget):
    def __init__(self, route: models.Route, *children: Widget, name = None, id = None, classes = None, disabled = False) -> None:
        self.route = route
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)

    def compose(self) -> ComposeResult:
        # Didn't find a connection for route
        if not self.route.found_connection:
            yield Label(f"Weren't able to connect {self.route.start.name} and {self.route.destination.name}", classes="align-center-middle")
            return
            
        yield RouteHeaderWidget(self.route)
        yield ConnectionTableWidget(self.route)


class RouteHeaderWidget(Widget):
    def __init__(self, route: models.Route, *children: Widget, name = None, id = None, classes = None, disabled = False) -> None:
        self.route = route
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)

    def compose(self) -> ComposeResult:
        yield Label(f"{self.route.start.name} -> {self.route.destination.name}")
        yield Label("Direct connection" if self.route.only_direct_routes else "No direct connection")
        yield Label(f"Coverage: {utils.parse_procent(self.route.best_coverage) if self.route.best_coverage else '100%'} SBB")
        yield Label(f"Connections: {len(self.route.connections)}")

class ConnectionTableWidget(Widget):
    def __init__(self, route: models.Route, *children: Widget, name = None, id = None, classes = None, disabled = False) -> None:
        self.route = route
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None: 
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        if self.route.only_direct_routes:
            table.add_columns("Start", "Destination", "Departure", "Arrival", "Duration", "Transfers")
            for connection in self.route.connections:
                table.add_row(
                    connection._from.station.name, 
                    connection.to.station.name,
                    connection._from.departure,
                    connection.to.arrival,
                    str(utils.parse_duration(connection.duration)),
                    connection.transfers,
                )
        else:
            table.add_columns("Start", "Destination", "Departure", "Arrival", "Duration", "Transfers", "Coverage")
            for connection in self.route.connections:
                table.add_row(
                    connection._from.station.name, 
                    connection.to.station.name,
                    connection._from.departure,
                    connection.to.arrival,
                    str(utils.parse_duration(connection.duration)),
                    connection.transfers,
                    utils.parse_procent(connection.coverage)
                )

