#!/usr/bin/env python3
""" TransportApp """

__author__ = "Aghrabi Carim, Zambelli Adrian, Schmid Aaron"
__version__ = "1.0.0"

from textual.widget import Widget
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label


class TransportWelcome(Widget):
    def compose(self) -> ComposeResult:
        with Container(classes="align-center-middle"):
            yield Label("Welcome, this app uses shortcuts or the mouse to navigate!")
            yield Label("(N) Start by creating a new trip!")
            yield Label("(D) Go into connection details")
            yield Label("(K) Check basic functionality (R 1.2.1)")
