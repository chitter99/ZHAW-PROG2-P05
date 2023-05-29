#!/usr/bin/env python3
""" TransportApp """

__author__ = "Aghrabi Carim, Zambelli Adrian, Schmid Aaron"
__version__ = "1.0.0"

from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Label, DataTable

from ... import models, utils


class RouteWidget(Widget):
    def __init__(
        self,
        route: models.Route,
        *children: Widget,
        name=None,
        id=None,
        classes=None,
        disabled=False,
    ) -> None:
        self.route = route
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )

    def on_mount(self) -> None:
        self.query_one(DataTable).focus()

    def compose(self) -> ComposeResult:
        # Didn't find a connection for route
        if not self.route.found_connection:
            yield Label(
                f"Weren't able to connect {self.route.start.name} and {self.route.destination.name}",
                classes="align-center-middle",
            )
            return

        yield RouteHeaderWidget(self.route)
        yield ConnectionTableWidget(self.route)


class RouteHeaderWidget(Widget):
    def __init__(
        self,
        route: models.Route,
        *children: Widget,
        name=None,
        id=None,
        classes=None,
        disabled=False,
    ) -> None:
        self.route = route
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )

    def compose(self) -> ComposeResult:
        yield Label(f"{self.route.start.name} -> {self.route.destination.name}")
        yield Label(
            "Direct connection"
            if self.route.only_direct_routes
            else "Alternative connection",
        )
        if self.route.best_coverage_providers:
            providers = [
                utils.parse_procent(provider.coverage) + " " + provider.name
                for provider in self.route.best_coverage_providers
            ]
            yield Label(f"Coverage: {' '.join(providers)}")
        if self.route.service_end_countries:
            yield Label(
                f"Service ends in: {', '.join([country.upper() for country in self.route.service_end_countries])}"
            )
        yield Label(f"Available connections: {len(self.route.connections)}")


class ConnectionTableWidget(Widget):
    def __init__(
        self,
        route: models.Route,
        *children: Widget,
        name=None,
        id=None,
        classes=None,
        disabled=False,
    ) -> None:
        self.route = route
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"

        columns = [
            "Start",
            "Destination"
            if self.route.only_direct_routes
            else "Alternative destination",
            "Departure",
            "Arrival",
            "Duration",
            "Transfers",
        ]

        if not self.route.only_direct_routes:
            columns += [
                "Coverage",
                "Ends in",
            ]

        table.add_columns(*columns)

        for connection in self.route.connections:
            row = [
                connection._from.station.name,
                connection.to.station.name,
                utils.prase_date(connection._from.departure),
                utils.prase_date(connection.to.arrival),
                str(utils.parse_duration(connection.duration)),
                connection.transfers,
            ]

            if not self.route.only_direct_routes:
                providers = [
                    utils.parse_procent(provider.coverage) + " " + provider.name
                    for provider in self.route.best_coverage_providers
                ]
                row += [
                    " ".join(providers),
                    connection.service_end_country.upper(),
                ]

            table.add_row(*row)
