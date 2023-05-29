from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Label, DataTable, TextLog

from ... import models, utils


class ConnectionOverviewWidget(Widget):
    def __init__(
        self,
        connection: models.RouteConnection,
        *children: Widget,
        name=None,
        id=None,
        classes=None,
        disabled=False,
    ) -> None:
        self.connection = connection
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )

    def compose(self) -> ComposeResult:
        yield Label(f"From: {self.connection._from.station.name}")
        yield Label(f"To: {self.connection.to.station.name}")
        yield Label(f"Transfers: {self.connection.transfers}")
        yield Label(f"Travel time: {utils.parse_duration(self.connection.duration)}")
        yield Label(
            "Direct connection"
            if self.connection.direct_connection
            else "Connection via alternative station"
        )
        if not self.connection.direct_connection:
            yield Label(
                f"Continue with provider: {self.connection.providers[1].name} ({self.connection.providers[1].url})"
            )
            yield ConnectionNotDirectInfoWidget(self.connection)


class ConnectionNotDirectInfoWidget(Widget):
    def __init__(
        self,
        connection: models.RouteConnection,
        *children: Widget,
        name=None,
        id=None,
        classes=None,
        disabled=False,
    ) -> None:
        self.connection = connection
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )

    def compose(self) -> ComposeResult:
        yield TextLog()

    def on_mount(self) -> None:
        text_log = self.query_one(TextLog)
        text_log.write(
            f"""For this trip no direct connection could be found! 
This is a alternative connection via {self.connection.to.station.name}.
To continue the trip please check further connection with {self.connection.providers[1].name}. 
Check their website on {self.connection.providers[1].url}""",
            shrink=True,
        )
        text_log.wrap = True


class ConnectionSectionsWidget(Widget):
    def __init__(
        self,
        connection: models.RouteConnection,
        *children: Widget,
        name=None,
        id=None,
        classes=None,
        disabled=False,
    ) -> None:
        self.connection = connection
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns(
            "Departure",
            "Destination",
            "Departure Time",
            "Arrival Time",
            "Platform",
            "Train",
            "Walk",
        )

        for section in self.connection.sections:
            arrival = section.arrival
            departure = section.departure
            journey = section.journey

            arrival_time = utils.prase_date(arrival.arrival) if arrival else ""
            departure_time = utils.prase_date(departure.departure) if departure else ""
            train = journey.number if journey else ""
            platform = departure.platform if departure else ""
            walk = section.walk.get("duration", "") or "" if section.walk else ""

            if walk != "":
                walk = str(round(int(walk) / 60)) + "min"

            table.add_row(
                departure.station.name if departure else "",
                arrival.station.name if arrival else "",
                departure_time,
                arrival_time,
                platform,
                train,
                walk,
            )
