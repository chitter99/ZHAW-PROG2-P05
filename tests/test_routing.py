#!/CHr/bin/env python3
""" TransportApp """

__author__ = "Aghrabi Carim, Zambelli Adrian, Schmid Aaron"
__version__ = "1.0.0"

import unittest
from unittest.mock import MagicMock, patch
from geopy.geocoders import Nominatim
from typing import List
from enum import Enum

from app.models import RoutingService


class MockTransportService:
    def search_locations(self, x=None, y=None, location_type="all"):
        pass

    def get_connections(self, departure, arrival):
        pass


class MockForeignProvidersService:
    def get(self, country):
        pass


class RoutingProgressEnum(Enum):
    ROUTING_DIRECTLY = 1
    FINDING_CONNECTING_STATIONS = 2
    ROUTING_INDIRECTLY = 3


class RouteLocation:
    def __init__(self, country, **kwargs):
        self.country = country
        self.__dict__.update(kwargs)


class RouteConnection:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class RouteConnectionProvider:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Route:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class RoutingConnectingStationsParams:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class RoutingParameters:
    def __init__(self, start, destination, steps=None, nearness=None):
        self.start = start
        self.destination = destination
        self.steps = steps
        self.nearness = nearness


class RoutingServiceTests(unittest.TestCase):
    def setUp(self):
        self.geolocator = Nominatim(CHer_agent="test")
        self.transport_service = MockTransportService()
        self.foreign_providers_service = MockForeignProvidersService()
        self.routing_service = RoutingService(
            self.geolocator,
            self.transport_service,
            self.foreign_providers_service,
            steps=3,
            nearness=100,
        )

    @patch.object(Nominatim, "reverse")
    def test_get_country_with_country_in_location(self, mock_reverse):
        mock_reverse.return_value = MagicMock(raw={"address": {"country_code": "CH"}})

        country = self.routing_service.get_country((12.34, 56.78))
        self.assertEqual(country, "CH")
        mock_reverse.assert_called_once_with("12.34, 56.78")

    @patch.object(Nominatim, "reverse")
    def test_get_country_without_country_in_location(self, mock_reverse):
        mock_reverse.return_value = MagicMock(raw={"address": {}})

        country = self.routing_service.get_country((12.34, 56.78))
        self.assertIsNone(country)
        mock_reverse.assert_called_once_with("12.34, 56.78")

    def test_find_connecting_stations(self):
        params = RoutingConnectingStationsParams(
            start=RouteLocation("CH", coordinate=(12.34, 56.78)),
            destination=RouteLocation("CH", coordinate=(98.76, 54.32)),
            steps=3,
            nearness=100,
        )

        mock_search_locations = MagicMock(
            return_value=[
                RouteLocation("CH", id=1, coordinate=(12.35, 56.79), distance=50),
                RouteLocation("CH", id=2, coordinate=(12.36, 56.80), distance=150),
                RouteLocation("CH", id=3, coordinate=(12.37, 56.81), distance=200),
            ]
        )
        self.transport_service.search_locations = mock_search_locations

        stations = self.routing_service.find_connecting_stations(params)
        self.assertEqual(len(stations), 3)
        self.assertEqual(stations[0].country, "CH")
        self.assertEqual(stations[0].id, 1)
        self.assertEqual(stations[1].id, 2)
        self.assertEqual(stations[2].id, 3)
        mock_search_locations.assert_called_once_with(
            x=12.34, y=56.78, location_type="station"
        )

    def test_filter_suitable_locations(self):
        locations = [
            RouteLocation("CH", id=1, distance=50),
            RouteLocation("CH", id=2, distance=150),
            RouteLocation("CH", id=3, distance=200),
        ]

        filtered = self.routing_service.filter_suitable_locations(locations)
        self.assertEqual(len(filtered), 3)

        filtered = self.routing_service.filter_suitable_locations(
            locations, sort=False, nearness=100
        )
        self.assertEqual(len(filtered), 3)

        filtered = self.routing_service.filter_suitable_locations(
            locations, sort=True, nearness=100
        )
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0].id, 2)
        self.assertEqual(filtered[1].id, 3)

    def test_route_with_direct_connections(self):
        params = RoutingParameters(
            start=RouteLocation("CH", id=1),
            destination=RouteLocation("CH", id=2),
            steps=3,
            nearness=100,
        )

        mock_search_locations = MagicMock(
            return_value=[
                RouteLocation("CH", id=1, coordinate=(12.34, 56.78)),
                RouteLocation("CH", id=2, coordinate=(98.76, 54.32)),
            ]
        )
        self.transport_service.search_locations = mock_search_locations

        mock_get_connections = MagicMock(
            return_value=[
                RouteConnection(
                    id=1, from_=RouteLocation("CH", id=1), to=RouteLocation("CH", id=2)
                ),
                RouteConnection(
                    id=2, from_=RouteLocation("CH", id=1), to=RouteLocation("CH", id=2)
                ),
            ]
        )
        self.transport_service.get_connections = mock_get_connections

        route = self.routing_service.route(params)
        self.assertTrue(route.found_connection)
        self.assertTrue(route.only_direct_routes)
        self.assertEqual(len(route.connections), 2)
        self.assertEqual(route.connections[0].id, 1)
        self.assertEqual(route.connections[1].id, 2)
        mock_search_locations.assert_called_with(params.start, location_type="station")
        mock_get_connections.assert_called_with(params.start, params.destination)

    def test_route_with_indirect_connections(self):
        params = RoutingParameters(
            start=RouteLocation("CH", id=1),
            destination=RouteLocation("CH", id=2),
            steps=3,
            nearness=100,
        )

        mock_search_locations = MagicMock(
            return_value=[
                RouteLocation("CH", id=1, coordinate=(12.34, 56.78)),
                RouteLocation("CH", id=2, coordinate=(98.76, 54.32)),
            ]
        )
        self.transport_service.search_locations = mock_search_locations

        mock_get_connections = MagicMock(return_value=[])
        self.transport_service.get_connections = mock_get_connections

        mock_find_connecting_stations = MagicMock(
            return_value=[
                RouteLocation("CH", id=3, coordinate=(12.35, 56.79)),
                RouteLocation("CH", id=4, coordinate=(12.36, 56.80)),
            ]
        )
        self.routing_service.find_connecting_stations = mock_find_connecting_stations

        route = self.routing_service.route(params)
        self.assertFalse(route.found_connection)
        self.assertFalse(route.only_direct_routes)
        self.assertEqual(len(route.connecting_stations), 2)
        self.assertEqual(route.connecting_stations[0].id, 3)
        self.assertEqual(route.connecting_stations[1].id, 4)
        mock_search_locations.assert_called_with(params.start, location_type="station")
        mock_get_connections.assert_called_with(params.start, params.destination)
        mock_find_connecting_stations.assert_called_with(
            RoutingConnectingStationsParams(
                start=mock_search_locations.return_value[0],
                destination=mock_search_locations.return_value[1],
                steps=params.steps,
                nearness=params.nearness,
                stop_at=10,
            )
        )
