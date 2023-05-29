from textual.app import App, ComposeResult
from textual.color import Color
from textual.reactive import reactive
from textual.widgets import Header, Footer, Static, DataTable

from .. import models, services
from . import screens, widgets


class Bar(Static):
    pass


class TransportApp(App):
    CSS_PATH = "styles.css"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("n", "new_trip", "New trip"),
        ("d", "trip_detail", "Connection details"),
        ("k", "push_screen('key_stations')", "Key stations (Req 1.2.1)"),
    ]

    current_route = reactive(None)

    def __init__(
        self,
        routing_service: services.RoutingService,
        location_autocomplet_service: services.LocationAutocompletService,
        key_station_service: services.KeyStationsService,
        driver_class=None,
        css_path=None,
        watch_css=False,
    ):
        self.routing_service = routing_service
        self.location_autocomplet_service = location_autocomplet_service
        self.key_station_service = key_station_service
        super().__init__(driver_class, css_path, watch_css)

    def on_mount(self) -> None:
        self.install_screen(screens.CreateNewRouteScreen, name="create_new_route")
        self.install_screen(screens.KeyStationsScreen, name="key_stations")

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield widgets.TransportWelcome()

    def action_new_trip(self) -> None:
        def update_route(route):
            self.current_route = route

        self.push_screen("create_new_route", update_route)

    def action_trip_detail(self) -> None:
        if self.current_route:
            table = self.query_one(DataTable)
            self.push_screen(
                screens.ConnectionDetailsScreen(
                    self.current_route.connections[table.cursor_row]
                )
            )

    def action_quit(self) -> None:
        self.exit(0)

    def action_add_bar(self, color: str) -> None:
        bar = Bar(color)
        bar.styles.background = Color.parse(color).with_alpha(0.5)
        self.mount(bar)
        self.call_after_refresh(self.screen.scroll_end, animate=False)

    def watch_current_route(self, route: models.Route):
        if not route:
            return

        # We need to catch the NoMatches exception here to prevent errors if the element has already been removed
        try:
            self.query_one(widgets.TransportWelcome).remove()
        except:
            pass
        # We also catch NoMatches exception here if the element has never been mounted
        try:
            self.query_one(widgets.RouteWidget).remove()
        except:
            pass

        self.mount(widgets.RouteWidget(route))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.push_screen(
            screens.ConnectionDetailsScreen(
                self.current_route.connections[event.cursor_row]
            )
        )
