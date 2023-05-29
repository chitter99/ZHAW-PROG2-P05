#!/usr/bin/env python3
""" TransportApp """

__author__ = "Aghrabi Carim, Zambelli Adrian, Schmid Aaron"
__version__ = "1.0.0"

from .base import BaseService
from .routing import RoutingService
from .. import utils


class CLIService(BaseService):
    def __init__(self, routing_service: RoutingService) -> None:
        self.routing = routing_service
        self.current_route = None
        super().__init__()

    def print_header(self):
        print("###")
        print("# Europe Public Transport Router")
        print("")

    def print_usage(self):
        if self.current_route:
            print(
                f"[#] Current trip: {self.current_route.start} -> {self.current_route.dest}"
            )
            print("")

        print("Choose a option:")
        print("1) Plan a new trip")

        if self.current_route:
            print("2) Print trip details")
            print("3) Print trip connection details")

        print("q) Exit")

    def print_current_route(self):
        route = self.current_route
        print("Route Information:")
        print(f"Start: {route.start}")
        print(f"Destination: {route.dest}")
        print(f"Found Connection: {'Yes' if route.found_connection else 'No'}")
        if route.found_connection:
            print(f"Direct Route: {'Yes' if route.direct_route else 'No'}")
            if not route.direct_route:
                print(f"Nearest Station: {route.nearest_startion}")
            print(f"SBB Coverage: {route.coverage * 100}%")
            print("Connections:")
            for connection in route.connections:
                duration = utils.parse_duration(connection["duration"])
                print(
                    f"From: {connection['from']['station']['name']} To: {connection['to']['station']['name']} Travel Time: {duration}m"
                )

    def create_new_route(self):
        start = input("Enter the start location: ")
        dest = input("Enter the destination location: ")
        print("Calculating best route, this could take some time...")
        print("")
        self.current_route = self.routing.route(start, dest)
        self.print_current_route()

    def print_connection(self):
        pass

    def run(self):
        self.print_header()

        while True:
            self.print_usage()
            choice = input("Option: ").lower()

            if choice == "q":
                print("Goodbye!")
                break

            if choice == "1":
                self.create_new_route()
                continue

            if choice == "2":
                self.print_current_route()
                continue

            if choice == "3":
                self.print_connection()
                continue

            print("Unknown option, please retry!")
