#!/usr/bin/env python3
""" TransportApp """

__author__ = "Aghrabi Carim, Zambelli Adrian, Schmid Aaron"
__version__ = "1.0.0"

from typing import List
from textual.app import ComposeResult
from textual.widgets import Label, ProgressBar, Button
from textual.screen import Screen
from textual.reactive import reactive
from textual.widgets import Header, DataTable
from textual.containers import Center, Middle
from textual.worker import Worker, WorkerState

from .base import BaseScreen
from ... import models, services


class KeyStationsScreen(BaseScreen):
    BINDINGS = [
        ("r", "reload", "Check key stations"),
    ]

    tracking = reactive([])

    def on_mount(self) -> None:
        self.tracking = self.app.key_station_service.key_stations_tracking

    def action_reload(self) -> None:
        def callback(tracking: List[models.KeyStationTracking]):
            self.tracking = tracking

        self.app.push_screen(LoadingKeyStationsScreen(), callback)

    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield Label("This table contains key stations and their tracking info")
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("Start", "Station", "Reachable", "Latitude", "Longitude")

    def watch_tracking(self):
        table = self.query_one(DataTable)
        table.clear(columns=False)

        for station in self.tracking:
            table.add_row(
                station.start,
                station.station,
                "Yes" if station.reachable else "No",
                {str(station.latitude)} if station.latitude else "",
                {str(station.longitude)} if station.longitude else "",
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        event.stop()


class LoadingKeyStationsScreen(Screen):
    def on_mount(self) -> None:
        self.run_worker(self.lookup_key_stations, exclusive=True)

    def lookup_key_stations(self) -> List[models.KeyStationTracking]:
        return self.app.key_station_service.refetch_tracking(self.progress_callback)

    def progress_callback(self, total, progress):
        self.query_one(ProgressBar).update(total=total, progress=progress)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.state == WorkerState.SUCCESS:
            self.dismiss(event.worker.result)

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Middle():
                yield Label("Fetching key station connections", id="loading-text")
                yield ProgressBar()
